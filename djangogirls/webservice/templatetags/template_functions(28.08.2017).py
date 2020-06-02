from django import template
from django.template import Template,Context
import os.path
from django.contrib.auth.models import User
from adminpanel.models import SubscribeUser,Logo,Footerlinks,Cms,Faq,UserWithroles,UserProfile,Category,ProductReview,FavouriteProducts,ProductDetails,PostJobInterest,ProductCategory,AcceptJob
from django.db import connection
from django.db.models import Avg

register = template.Library()
@register.simple_tag
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@register.simple_tag
def get_subscribeinfo(userid):
    if SubscribeUser.objects.filter(user_id=userid).exists():
        subinfo = SubscribeUser.objects.get(user_id=userid)
    else :
        subinfo=""
    return subinfo

@register.simple_tag
def get_logo():
    logo = Logo.objects.get(pk=1)
    return logo

@register.simple_tag
def get_finddefender():
    parent_categories=Category.objects.filter(parentid=0).order_by('category_name')[0:20] 
    return parent_categories
    
@register.simple_tag
def get_parent_category():
     all_parent_categories=Category.objects.filter(parentid=0).order_by('category_name')
     return all_parent_categories
    
@register.simple_tag
def get_footerlinks():
    footer_links = Footerlinks.objects.all()
    return footer_links

@register.simple_tag      
def show_footer_menu():
 all_cms = Cms.objects.all().order_by('id')
 return(all_cms)

@register.simple_tag      
def show_faq(category_id):
 faq=Faq.objects.filter(faqcategory_id=category_id,is_active=1)
 return(faq)

@register.simple_tag      
def get_user_roles(user_id):
 user_roles = UserWithroles.objects.get(user_id=user_id)
 return(user_roles)

@register.simple_tag      
def get_user(user_id):
 user = User.objects.get(pk=user_id)
 return(user)

@register.simple_tag      
def get_userprofile(user_id):
 userprofile = UserProfile.objects.get(user_id=user_id)
 return(userprofile)

@register.simple_tag      
def get_userdetails(user_id):
 cursor = connection.cursor()
 cursor.execute("select u.*,up.* from auth_user as u INNER JOIN adminpanel_userprofile as up ON u.id = up.user_id where u.id ='"+str(user_id)+"'" ) 
 userprofile = dictfetchall(cursor)
 return(userprofile[0])

@register.simple_tag      
def get_subcategory(parent_id):
 subcategory=Category.objects.filter(parentid=parent_id).order_by('category_name')
 return(subcategory)

@register.simple_tag      
def get_categoryproducts(category_id):
 cursor = connection.cursor()
 cursor.execute("select p.*,pd.* from adminpanel_productdetails as pd INNER JOIN adminpanel_productcategory as pc"
 " ON pd.product_id = pc.product_id INNER JOIN adminpanel_products as p ON pd.product_id = p.id where pc.category_id ="+str(category_id)+"ORDER BY p.id Desc LIMIT 3" ) 
 result_list = dictfetchall(cursor)
 return(result_list)

@register.simple_tag   
def get_productdetails(product_id):
 cursor = connection.cursor()
 cursor.execute("select p.*,pd.* from adminpanel_productdetails as pd INNER JOIN adminpanel_products as p ON pd.product_id = p.id where p.id ="+str(product_id)) 
 result_list = dictfetchall(cursor)
 return(result_list[0])

@register.simple_tag      
def get_categoryservices(category_id):
 cursor = connection.cursor()
 cursor.execute("select s.*,sd.* from adminpanel_servicesdetails as sd INNER JOIN adminpanel_services as s ON sd.service_id = s.id where s.category_id ="+str(category_id)+"ORDER BY s.id Desc LIMIT 3")
 result_list = dictfetchall(cursor)
 return(result_list)

@register.simple_tag      
def get_mapmarkers(lists):
 markers = []   
 import json
 for list in lists:
       
    file_info = {}
    file_info['latitude'] = list['latitude']
    file_info['longitude'] = list['longitude']
    file_info['location'] = list['location']
    file_info['medium_pic'] = list['medium_pic']
    file_info['slug'] = list['slug']
    file_info['addedby_id'] = list['addedby_id']
    file_info['regularprice'] = list['regularprice']
    userprofile = UserProfile.objects.get(user_id=list['addedby_id'])
    file_info['cover_pic'] = userprofile.medium_pic
    markers.append(file_info)
    
 return(json.dumps(markers))

@register.simple_tag      
def show_productrating(product_id):
    if ProductReview.objects.filter(product_id=product_id,is_approved=1).exists():
        all_over_rating=ProductReview.objects.filter(product_id=product_id,is_approved=1).aggregate(Avg('rating'))
    else:
        all_over_rating="0"
    return(all_over_rating)   

@register.simple_tag      
def show_favourite(product_id,user_id):
    if FavouriteProducts.objects.filter(product_id=product_id,user_id=user_id).exists():
        favourite="1"
    else:
        favourite="0"
    return(favourite) 

@register.simple_tag      
def favourite_products(user_id):
    if FavouriteProducts.objects.filter(user_id=user_id).exists():
        cursor = connection.cursor()
        cursor.execute("select p.*,pd.* from adminpanel_productdetails as pd"
        " INNER JOIN adminpanel_products as p ON pd.product_id = p.id" 
        " INNER JOIN adminpanel_favouriteproducts as fp ON p.id = fp.product_id" 
        " where fp.user_id ="+str(user_id)+" ORDER BY p.id Desc LIMIT 4")
        result_list = dictfetchall(cursor)
        return result_list
    else:
        result_list=""
        return(result_list)
    

@register.simple_tag
def cms_details(cms_id):
    if Cms.objects.filter(id=cms_id).exists():
               slug_details = Cms.objects.get(id=cms_id)
               t = Template(slug_details.text)
               c = Context({})
               msg_html = t.render(c)
               return (msg_html)
    else :
        msg_html = "No Details"
        return (msg_html)

@register.simple_tag      
def common_products():
    cursor = connection.cursor()
    cursor.execute("select p.*,pd.*,u.first_name,u.last_name,up.medium_pic as userpic,up.user_id from adminpanel_productdetails as pd"
    " INNER JOIN adminpanel_products as p ON pd.product_id = p.id" 
    " INNER JOIN adminpanel_userprofile as up ON pd.addedby_id = up.user_id" 
    " INNER JOIN auth_user as u ON u.id = up.user_id ORDER BY p.id Desc LIMIT 4")
    result_list = dictfetchall(cursor)
    return(result_list)

@register.simple_tag      
def common_services():
    cursor = connection.cursor()
    cursor.execute("select s.*,sd.* from adminpanel_servicesdetails as sd INNER JOIN adminpanel_services as s ON sd.service_id = s.id ORDER BY s.id Desc LIMIT 4")
    result_list = dictfetchall(cursor)
    return(result_list)

@register.simple_tag      
def is_vendorproduct(user_id):
    if ProductDetails.objects.filter(addedby_id=user_id).exists():
        is_product=1
    else:
        is_product=0
    return(is_product) 

@register.simple_tag      
def show_vandor_product(user_id):
    if ProductDetails.objects.filter(addedby_id=user_id).exists():
        vandor_products=ProductDetails.objects.filter(addedby_id=user_id)
    else:
        vandor_products="0"
    return(vandor_products)     

@register.simple_tag      
def get_particular_category(category_id):
 cursor = connection.cursor()
 cursor.execute("select * from adminpanel_category where id ='"+str(category_id)+"'" ) 
 cat = dictfetchall(cursor)
 return(cat[0])  

@register.simple_tag      
def get_category_postjob(post_id):
    
  postjob_category=PostJobInterest.objects.filter(postjob_id=post_id)
  
  return(postjob_category)

@register.simple_tag
def get_products_parent_category():
     all_category=[]
    #existing_product_category = ProductCategory.objects.exclude(~Q(id=0))
     cursor = connection.cursor()
     cursor.execute("select category_id from adminpanel_productcategory GROUP BY adminpanel_productcategory.category_id")
     #print(cursor.query);
     existing_product_category = dictfetchall(cursor)
     #print(existing_product_category)
     for eproduct_category in existing_product_category:
      #print(eproduct_category['category_id'])
       all_parent_categories=Category.objects.filter(parentid=0,id=eproduct_category['category_id']).order_by('category_name')
       for all_parent_category in all_parent_categories :
        print(all_parent_category.category_name)
        import json
        jsonObj = {}
        jsonObj['category_name'] = all_parent_category.category_name
        jsonObj['slug'] = all_parent_category.slug
        jsonObj['id'] = all_parent_category.id
        all_category.append(jsonObj)
        print(all_category)
     return (all_category)

@register.filter
def times(value):
    return range(value)
        

