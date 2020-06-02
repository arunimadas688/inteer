from adminpanel.models import *
def categories_processor(request):
  prime_categories = Category.objects.filter(parentid=0,isfeatured=1)[0:3]            
  return {'prime_categories': prime_categories}


  