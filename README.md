ClearConf is a Python configuration management library that provides a clean, hierarchical way to define and manage configurations through Python classes.

Defining configurations in python makes them
- **easy to access**: you can read configuration with a simple `import` statement
- **flexible**: compositionality, inerhitance and other python features are integrated into clearconf
- **customizable**: the framework allows to easily define new class-method and Types to add custom functionalities

## Core Concepts

### BaseConfig Class
The base class that all configurations must inherit from. It provides the foundation for hierarchical configuration management.

```python
from clearconf import BaseConfig

class MyConfig(BaseConfig):
    pass
```
When your root config subclass `BaseConfig` all nested classes will be automatically set to subclass `BaseConfig`. This will add to each of them a series of functionalities such as serialization functions and the ability to set values through the command line.

### Configuration Structure
Configurations are defined using nested Python classes that inherit from 

`BaseConfig`

. Each class represents a configuration section.

```python
class Config(BaseConfig):
    seed = 1234
    
    class Model:
        num_layers = 16
        
        class Params:
            learning_rate = 0.001
```

## Features

### 1. Dynamic Values
Values that need to be computed can use the `[eval]` prefix:

```python
class Config(BaseConfig):
    model_name = "resnet"
    checkpoint_path = '[eval]f"checkpoints/{cfg.model_name}.pt"'
```

Dynamic values are resolved at run time. This means that in the following case:
```python
class CommonConfig(BaseConfig):
        
    class Logging:
        exp_dir:str = '[eval]f"{cfg.Method.name}_{cfg.Data.name}"'

    class Method:
        device:str = "cuda:0"


class Config(CommonConfig):

    class Method(CommonConfig.Method, MyMethod):
        name = 'MethodA'
        checkpoint = project_root / '../checkpoints/method.pt'

class MyDataset(BaseConfig):
    batch_size = 128
    name = '[eval]f"DatasetA_{cls.batch_size}"'

Config.Data = MyDataset
Config.Logging.exp_dir
```
The attribute `Config.Logging.exp_dir` would be resolved to `'MethodA_DatasetA_128'`

### 2. Hidden Fields
Fields that should be ignored by clearconf functions (e.g. `to_dict`) can be marked as

`Hidden`

:

```python
from clearconf import BaseConfig, Hidden

class Config(BaseConfig):
    api_key: Hidden = "secret123"
```

### 3. Interactive Configuration 
Fields that require user input can be marked with 

`Prompt`

:

```python
from clearconf import BaseConfig, Prompt

class Config(BaseConfig):
    dataset_path: Prompt = "path/to/default"
```

This will open an editor and ask the user to input a value.

### 4. Class Inheritance
Configurations can inherit from implementation classes to provide direct access to configuration values:

```python
from models import MyModel

class Config(BaseConfig):
    class Model(MyModel):
        num_layers = 16
        hidden_size = 256
```

An instance of the implementation class can then be obtained through the configuration:
```python
model = Config.Model()
```

The instance will have direct access to the values provided from inside the configuration:
```python
class MyMethod:
    def __init__(self):
        print(self.num_layer)
        print(self.hidden_size)
```

### 5. Configuration Methods

These methods, set as Hidden, are automatically added to all BaseConfig configurations.

#### to_dict()
Converts the configuration to a dictionary:

```python
config_dict = Config.to_dict()
```

#### to_flat_dict()
Converts the configuration to a flattened dictionary with dot notation:

```python
flat_dict = Config.to_flat_dict()
# {'Model.num_layers': 16, 'Model.hidden_size': 256}
```

#### to_json()
Serializes the configuration to JSON:

```python
json_str = Config.to_json()
```

### 6. Configuration Access

Configurations can be accessed using dot notation:

```python
# Access nested values
learning_rate = Config.Model.Params.learning_rate

# Access parent configuration
model = Config.Model()  # Creates model instance with config values
```

### 7. Command Line Integration

The library supports automatic command-line argument parsing to override configuration values:

```bash
python train.py --Model models.MyModel --Model.num_layers 32 --learning_rate 0.0005
```

## Example Configuration

```python
from clearconf import BaseConfig, Hidden, Prompt
from models import ResNet
from datasets import ImageDataset

class TrainingConfig(BaseConfig):
    seed = 1234
    device = "cuda"
    
    class Model(ResNet):
        name = "resnet50"
        num_classes = 10
        pretrained = True
        checkpoint: Hidden = "checkpoints/latest.pt"
        
    class Data:
        dataset = ImageDataset
        root_dir: Prompt = "./data"
        
        class Params:
            batch_size = 32
            num_workers = 4
            
    class Optimizer:
        name = "adam"
        learning_rate = 0.001
```
