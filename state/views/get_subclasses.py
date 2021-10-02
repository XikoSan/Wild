from django.apps import apps


def get_subclasses(abstract_class):
   result = []
   for model in apps.get_app_config('gamecore').get_models():
      if issubclass(model, abstract_class) and model is not abstract_class:
           result.append(model)
   return result