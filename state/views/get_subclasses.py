from django.apps import apps

# получает всех НЕ абстрактных потомков класса
# если нужно с абстрактными - используй Obj.__subclasses__()
def get_subclasses(abstract_class):
   result = []
   for model in apps.get_app_config('gov').get_models():
      if issubclass(model, abstract_class) and model is not abstract_class:
           result.append(model)
   return result