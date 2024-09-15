import importlib
from tortoise import Tortoise, Model
from webweaver_node.config import all_models, POSTGRES_DB

async def init(namespace):
    await Tortoise.init(db_url=POSTGRES_DB, modules={'models': all_models})
    await Tortoise.generate_schemas()
    import_tortoise_models(all_models, namespace)



def import_tortoise_models(model_modules, namespace):
    for module_path in model_modules:
        module = importlib.import_module(module_path)
        s = f"from {module_path} import"
        tables = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Model) and attr != Model:
                namespace[attr_name] = attr
                tables.append(f", \033[1m{attr_name}\033[0m")
        print(f"{s} {', '.join(tables)}")



# def import_tortoise_models(model_modules, namespace):
#     for module_path in model_modules:
#         module = importlib.import_module(module_path)
#         for attr_name in dir(module):
#             attr = getattr(module, attr_name)

#             if isinstance(attr, type) and issubclass(attr, Model) and attr != Model:
#                 namespace[attr_name] = attr
#                 print(f"from {module_path} import \033[1m{attr_name}\033[0m")