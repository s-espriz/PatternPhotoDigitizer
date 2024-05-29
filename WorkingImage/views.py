from django.shortcuts import render
from django.urls import reverse_lazy
from django.urls import reverse
from django.views.generic import CreateView,DeleteView
from .models import Image
from pathlib import Path
from django.conf import settings
import PIL
from django.http import HttpResponseRedirect
import cv2
import ezdxf
from WorkingImage.functions import * 

def Index(request):
    return render(request, 'index.html')
class ImageAdding(CreateView):
    model = Image
    success_url = reverse_lazy('home')
    fields = ['img']
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
def Panel(request):
    images = Image.objects.filter(owner=request.user.id)
    total_images = images.count()
    context = {
        'total_images' : total_images,
        'images' : images,
    }
    return render(request, 'panel.html', context)
class DeleteView(DeleteView):
    model = Image
    success_url = reverse_lazy('panel')
def Optimize(request, pk):
    model = Image
    image = Image.objects.get(id=pk)
    image_optimized_url = image.optimized_url
    not_optimized = True
    if image_optimized_url == "none":
        not_optimized = True
    else:
        not_optimized = False
    image_optimized_url_dxf = f'{image_optimized_url}.dxf'
    user = request.user
    available = False
    if image.owner == user:
        available = True
    methods_spline_normal = False
    methods_spline_medium = False
    methods_spline_high = False
    if image.methods_spline == "normal":
        methods_spline_normal = True
        methods_spline_medium = False
        methods_spline_high = False
    elif image.methods_spline == "centripetal":
        methods_spline_normal = False
        methods_spline_medium = True
        methods_spline_high = False
    else:
        methods_spline_normal = False
        methods_spline_medium = False
        methods_spline_high = True
    context = {
        'image' : image,
        'image_optimized_url' : f'../../{image_optimized_url}',
        'image_optimized_url_dxf' : f'../../{image_optimized_url_dxf}',
        'not_optimized': not_optimized,
        'blur' : image.blur,
        'threshold_percentage' : image.threshold_percentage,
        'arz' : image.arz,
        'tool' : image.tool,
        'epsilon' : image.epsilon,
        'grid_size' : image.grid_size,
        'small_things' : image.small_things,
        'spline' : image.spline,
        'degree_threshold' : image.degree_threshold,
        'methods_spline_normal' : methods_spline_normal,
        'methods_spline_medium' : methods_spline_medium,
        'methods_spline_high' : methods_spline_high,
        'available' : available,
    }
    return render(request, 'optimize.html', context)
def Optimizing(request, pk):
    model = Image
    picture = Image.objects.get(id=pk)
    picture_name = picture.img.name
    picture_url = picture.img.url
    
    values = {
        'blur' : request.POST.get('blur'),
        'threshold_percentage' : request.POST.get('threshold_percentage'),
        'arz' : request.POST.get('arz'),
        'tool' : request.POST.get('tool'),
        'epsilon' : request.POST.get('epsilon'),
        'grid_size' : request.POST.get('grid_size'),
        'small_things' : request.POST.get('small_things'),
        'spline' : request.POST.get('spline'),
        'degree_threshold' : request.POST.get('degree_threshold'),
        'methods_spline' : request.POST.get('methods_spline'),
        'jpgname' : request.POST.get('jpgname'),
        'dxfname' : request.POST.get('dxfname'),
    }
    """ این ها مقادیر هستن """
    blur = values.get("blur")
    threshold_percentage = values.get("threshold_percentage")
    arz = values.get("arz")
    tool = values.get("tool")
    epsilon = values.get("epsilon")
    grid_size = values.get("grid_size")
    small_things = values.get("small_things")
    degree_threshold = values.get("degree_threshold")
    methods_spline = values.get("methods_spline")
    #jpg_name = values.get("jpgname")
    #dxf_name = values.get("dxfname")

    #if jpg_name == "":
    #    jpg_name = picture.id
    #if dxf_name == "":
    #    dxf_name = picture.id
    #------------
    #------------""" کاری به این نداشته باشید """
    spline_html = values.get("spline")
    #------------""" این بولین اصلی هستش """
    spline = False 
    if spline_html == "on":
        spline = True
    else :
        spline = False
    #------------""" از اینجا به بعد میتونید از اسم متغیر ها مطابق با عدد و پارامتری که داخل اینپوت وارد کردید استفاده کنید """
    #------------""" رو داخل فانکشنتون قرار بدید برای ورودیه عکس picture_url متغیر """
    #------------""" هستش jpg.png,... چون همون آدرس و مسیر """
    #------------""" که به کارتون میاد """
    #------------""" اگر هم میخواید از این کتابخانه استفاده کنید هم میشه """
    #--------------
    #-------جهت تست
    picture.blur = blur
    picture.threshold_percentage = threshold_percentage
    picture.arz = arz
    picture.tool = tool
    picture.epsilon = epsilon
    picture.grid_size = grid_size
    picture.small_things = small_things
    picture.degree_threshold = degree_threshold
    picture.methods_spline = methods_spline.lower()
    picture.spline = spline
    picture.save()
    def MainFunction(request="GET"):
        # loading image into cv2 array 
        img = cv2.imread(f'../media/{picture_name}')
        print(f'img is {img}')
        checking_image = create_cheching_image(image= img , threshold_percentage=threshold_percentage ,tool=float(tool), epsilon=int(epsilon) , blur_size= int(blur), grid_size_cm=float(grid_size), spline=spline , degree_treshold= int(degree_threshold) , small_things= int(small_things), spline_method = methods_spline.lower())
        dxf_doc = create_final_image(image= img , threshold_percentage=threshold_percentage ,tool=float(tool), epsilon=int(epsilon) , blur_size= int(blur), spline=spline , degree_treshold= int(degree_threshold) , small_things= int(small_things), spline_method = methods_spline.lower() )

        #------------------------
        #اینجا محل فانکشن اصلی شماست
        #------------------------
        from PIL import Image
        #------------------------
        #بخش مربوط به باز کردن و سیو عکس
        #با توجه به اسم فایلی که از قبل پرسیده شده
        #------------------------
        #جهت خواندن و ایمپورت کردن
        
        #---------------------------
        picture_name_final = picture_name.replace("/", "_")
        #جهت ذخیره
        #---------------------------
        cv2.imwrite(f'../media/pictures/optimized/{picture_name_final}', checking_image)
        picture.optimized_url = f"media/pictures/optimized/{picture_name_final}"
        picture.save()
        #---------------------------
        # اینم یه متهود دیگه
        #---------------------------
        #-------------""" 
        #img = Image.open(f'media/{picture_name}')
        #img.save(f'{os.path.expanduser("~/Desktop/")}{jpg_name}.jpg')
        #-------------"""
        #------------------------
        #-------هستش dxf اینم واسه فایل
        #------------------------
        dxf_doc.saveas(f'../media/pictures/optimized/{picture_name_final}.dxf')
        #-----------------------
    MainFunction()
    #-------------
    #فانکشن شما تا اینجاست
    return HttpResponseRedirect(f'../optimize/{pk}')
    
