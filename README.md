ClearConf is a Python configuration management library that provides a clean, hierarchical way to define and manage configurations through Python classes.

## Core Concepts

### BaseConfig Class
The base class that all configurations must inherit from. It provides the foundation for hierarchical configuration management.

```python
from clearconf import BaseConfig

class MyConfig(BaseConfig):
    pass
```

### Configuration Structure
Configurations are defined using nested Python classes that inherit from 

BaseConfig

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

### 1. Configuration Types

#### Static Values
Simple configuration values can be defined as class attributes:

```python
class Config(BaseConfig):
    batch_size = 32
    learning_rate = 0.001
```

#### Dynamic Values
Values that need to be computed can use the `[eval]` prefix:

```python
class Config(BaseConfig):
    model_name = "resnet"
    checkpoint_path = '[eval]f"checkpoints/{cfg.model_name}.pt"'
```

### 2. Hidden Fields
Fields that should not appear in serialized output can be marked with 

Hidden

:

```python
from clearconf import BaseConfig, Hidden

class Config(BaseConfig):
    api_key: Hidden = "secret123"
```

### 3. Interactive Configuration 
Fields that require user input can be marked with 

Prompt

:

```python
from clearconf import BaseConfig, Prompt

class Config(BaseConfig):
    dataset_path: Prompt = "path/to/default"
```

### 4. Class Inheritance
Configurations can inherit from implementation classes to provide direct access to configuration values:

```python
from models import MyModel

class Config(BaseConfig):
    class Model(MyModel):
        num_layers = 16
        hidden_size = 256
```

### 5. Configuration Methods

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
python train.py --Model.num_layers 32 --learning_rate 0.0005
```

## Best Practices

1. Use nested classes to organize related configuration parameters
2. Use type hints for better documentation
3. Use 

Hidden

 for sensitive information
4. Use `[eval]` for dynamic configuration values
5. Inherit from implementation classes when configuration values are tightly coupled
6. Place reusable configuration in base classes

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

andrearosasco: rewrite it using github markdown (this means you can use stuff like > [!NOTE] or > [!IMPORTANT]) also talk about compositionality of configs at runtime (e.g. the fact that you can do cfg.data = Data) and that cfg in Data eval string will evaluate with respect to the new root config. And also about the fact that you can do stuff like this python config.py --Method config.MyMethod. Also discuss both about Prompt and Hidden but they should be grouped under the same group of features. you can find a name that you want for it 

GitHub Copilot: # ClearConf Documentation

ClearConf is a Python configuration management library that provides a clean, hierarchical way to define and manage configurations through Python classes.

## Core Features

### Configuration Inheritance
Configurations are defined using nested Python classes that inherit from 

BaseConfig

:

```python
from clearconf import BaseConfig

class Config(BaseConfig):
    seed = 1234
    
    class Model:
        num_layers = 16
        hidden_size = 256
```

> [!NOTE]
> Classes nested inside a BaseConfig automatically inherit from it

### Dynamic Values & Runtime Composition

#### Dynamic Values
Values that need to be computed can use the `[eval]` prefix:

```python
class Config(BaseConfig):
    model_name = "resnet"
    save_path = '[eval]f"checkpoints/{cfg.model_name}.pt"'
```

#### Runtime Configuration Composition
Configurations can be composed at runtime:

```python
from data_config import DataConfig

class Config(BaseConfig):
    seed = 1234
    # Data config can be assigned later
    
# Runtime composition
Config.data = DataConfig
```

> [!IMPORTANT]  
> When using `[eval]` strings, 

cfg

 will evaluate relative to the root configuration, even in imported sub-configurations

### Special Field Types

Both 

Hidden

 and 

Prompt

 provide ways to handle special configuration values:

```python
from clearconf import BaseConfig, Hidden, Prompt

class Config(BaseConfig):
    api_key: Hidden = "secret123"  # Hidden from serialization
    dataset_path: Prompt = "default/path"  # Prompts for user input
```

### Implementation Inheritance 
Configurations can inherit from implementation classes:

```python
from models import ResNet

class Config(BaseConfig):
    class Model(ResNet):  # Direct inheritance from implementation
        num_layers = 16
        hidden_size = 256
```

This allows the object to directly access its arguments as follow:

```python
class ResNet:
    def __init__(self):
        # Access config values through self
        self.layers = [nn.Linear(self.hidden_size, self.hidden_size) 
                      for _ in range(self.num_layers)]
```

And allows the application code to instantiate the object as :

```python
# training.py
def train():
    ...
    # Creates ResNet instance with config values
    model = Config.Model()
    y = model(x)
```

### Command Line Integration

Configurations can be modified via command line arguments:

```bash
# Override configuration values
python train.py --Model.num_layers 32

# Load implementation class
python train.py --Method methods.MyMethod
```

## Configuration Methods

### to_dict()
Converts configuration to a dictionary:

```python
config_dict = Config.to_dict()
```

### to_flat_dict() 
Flattens configuration with dot notation:

```python
flat_dict = Config.to_flat_dict()
# {'Model.num_layers': 16, 'Model.hidden_size': 256}
```

### to_json()
Serializes to JSON:

```python
json_str = Config.to_json()
```

## Example Configuration

```python
from clearconf import BaseConfig, Hidden, Prompt
from models import ResNet

class TrainingConfig(BaseConfig):
    seed = 1234
    device = "cuda"
    
    class Model(ResNet):
        num_layers = 16
        checkpoint: Hidden = "checkpoints/latest.pt"
        data_path: Prompt = "./data"  # Will prompt user
        
        # Dynamic path based on configuration
        save_path = '[eval]f"outputs/{cfg.Model.num_layers}_layers/"'
```

> [!NOTE]
> The configuration system is designed to be both flexible at runtime and type-safe during development