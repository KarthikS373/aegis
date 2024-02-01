import torch
from torchvision import models
from PIL import Image
from hexbytes import HexBytes
from torch import nn
import numpy as np
from PIL import Image
from pyevmasm.evmasm import disassemble_hex, assemble_hex

SAFE_IDX = 4


def normalize_bytecode(bytecode):
    opcode_list = disassemble_hex(bytecode).split('\n')
    new_opcodes = []

    def is_odd(value):
        return (value % 2) != 0

    for opcode in opcode_list:
        if 'PUSH' in opcode:
            value = opcode.strip().split(' ')[-1]
            if 'PUSH1 ' in opcode:
                new_opcode = f'PUSH2 {value}00'
            elif 'PUSH2 ' in opcode:
                new_opcode = opcode
            else:
                cut_val = 5 if is_odd(len(value.replace('0x', ''))) else 6
                new_opcode = f'PUSH2 {value[:cut_val]}'
        else:
            new_opcode = opcode
        new_opcodes.append(new_opcode)

    hex_string = assemble_hex(new_opcodes[0])

    for elem in new_opcodes[1:]:
        hex_string += assemble_hex(elem).replace('0x', '')
        if 'PUSH' not in elem:
            assert len(elem.split(' ')) == 1
            hex_string += '0000'

    return hex_string




class Registry(dict):
    '''
    A helper class for managing registering modules, it extends a dictionary
    and provides register functions.
    Access of module is just like using a dictionary, eg:
        f = some_registry["foo_module"]
    '''

    # Instanciated objects will be empyty dictionaries
    def __init__(self, *args, **kwargs):
        super(Registry, self).__init__(*args, **kwargs)

    # Decorator factory. Here self is a Registry dict
    def register(self, module_name, module=None):

        # Inner function used as function call
        if module is not None:
            _register_generic(self, module_name, module)
            return

        # Inner function used as decorator -> takes a function as argument
        def register_fn(fn):
            _register_generic(self, module_name, fn)
            return fn

        return register_fn

def _register_generic(module_dict, module_name, module):
    assert module_name not in module_dict
    module_dict[module_name] = module

REGISTRY = Registry()


@REGISTRY.register('resnet')
class ResNetModel(nn.Module):
    def __init__(self, num_classes=5, classify=True):
        super(ResNetModel, self).__init__()
        self.resnet = models.resnet18(pretrained=True)

        if classify:
            self.resnet.fc = nn.Linear(512, num_classes)
        else:
            features = nn.ModuleList(self.resnet.children())[:-1]
            self.resnet = nn.Sequential(*features).append(nn.Flatten())

    def forward(self, inputs):
        return self.resnet(inputs)

    def get_layer_groups(self):
        linear_layers = [elem[1] for elem in filter(lambda param_tuple: 'fc' in param_tuple[0], self.resnet.named_parameters())]
        other_layers = [elem[1] for elem in filter(lambda param_tuple: 'fc' not in param_tuple[0], self.resnet.named_parameters())]
        param_groups = {
            'classifier': linear_layers,
            'feature_extractor': other_layers
        }
        return param_groups
    

def preprocess_bytecode(bytecode):
    normalized_bytecode = normalize_bytecode(bytecode)
    code = HexBytes(normalized_bytecode)
    image = np.frombuffer(code, dtype=np.uint8)
    sqrt_len = int(np.ceil(np.sqrt(image.shape[0])))
    image = np.pad(image, pad_width=((0, sqrt_len ** 2 - image.shape[0])))
    image = image.reshape((sqrt_len, sqrt_len))
    image = np.stack((image,) * 3, axis=-1)
    image = Image.fromarray(image)
    return image

def predict(bytecode):
    model = REGISTRY['resnet'](num_classes=5, classify=True)
    checkpoint = torch.load("model/weights.pkl", map_location=torch.device('cpu'))
      # Provide the path to your checkpoint file
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device('cpu')
    model.to(device)
    model.eval()

    with torch.no_grad():
        image = preprocess_bytecode(bytecode)
        image = torch.tensor(np.array(image)).permute(2, 0, 1).unsqueeze(0).float()
        image = image.to(device)
        output = model(image)
        prediction = torch.sigmoid(output) >= 0.5
        return prediction.cpu().numpy().tolist()


def reverse_engineer_one_hot_encoding(predictions):
    original_labels = []
    for i, row in enumerate(predictions):
        indices = np.where(row == 1)[0]  # Find indices of non-zero elements (predicted classes)
        original_label = []
        if len(indices) == 0:  # If all elements are zeros
            original_label.append(SAFE_IDX)  # Append SAFE_IDX
        else:
            for idx in indices:
                if idx >= SAFE_IDX:
                    original_label.append(idx + 1)  # Increment index if greater than or equal to SAFE_IDX
                else:
                    original_label.append(idx)
        original_labels.append(original_label)
        # print(f"Row {i + 1}: Predicted Label: {row}, Original Label: {original_label}")
    return original_labels
 