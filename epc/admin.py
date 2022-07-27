from django.contrib import admin
from epc.forms import *
from import_export.admin import ExportActionMixin


class ModelInline(admin.TabularInline):
    model = Model
    show_change_link = True
    extra = 1


class GenerationInline(admin.TabularInline):
    model = Generation
    show_change_link = True
    extra = 1


class ComponentInline(admin.TabularInline):
    model = Component
    show_change_link = True
    extra = 1


class PartGroupInline(admin.TabularInline):
    model = PartGroup
    show_change_link = True
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    inlines = [ModelInline, ]


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', )
    fields = ('brand', 'name', )
    list_filter = ('brand__name',)
    inlines = [GenerationInline, ]

    # def generation_link(self, obj):
    #     return '<a href="/admin/epc/generation/?model_id__exact={0}">Generations</a>'.format(obj.id)
    #
    # generation_link.allow_tags = True


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    # form = CustomGenerationAdminForm
    list_display = ('name', 'brand_name', 'model')
    fields = ('model', 'name')
    list_filter = ('model__name', 'model__brand__name')

    def brand_name(self, obj):
        return obj.model.brand.name

    brand_name.short_description = 'Brand'

    # class Media:
    #     js = ('epc/js/asyncSelectModels.js',)

    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     field = super(GenerationAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)
    #     print(db_field)
    #     if db_field.name == 'brand':
    #         field.queryset = field.queryset.filter(name__icontains='Tesla')
    #     return field
    
    def add_view(self, request, form_url='', extra_context=None):
        # for key, value in request.POST.items():
        #     print(f'Key: {key}')
        #     print(f'Value: {value}')
        # print(self.form.declared_fields)
        # self.form.base_fields['model'].queryset = Model.objects.filter(pk=request.POST.get('model'))
        # print(self.form.base_fields['model'].queryset)
        # print('ADD VIEW')
        return super(GenerationAdmin, self).add_view(request, form_url='', extra_context=None,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # arr = request.get_full_path().split('/')
        # print(arr[len(arr) - 3])
        # self.form = CustomGenerationAdminForm(initial={'brand': 'Tesla'})
        # print('CHANGE VIEW')
        return super().change_view(request, object_id, form_url, extra_context=extra_context,)


@admin.register(ComponentGroup)
class ComponentGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', )
    list_filter = ('name', )
    search_fields = ['name', '=code']
    inlines = [ComponentInline, ]

    # def model_name(self, obj):
    #     return obj.generation.model.name
    #
    # model_name.short_description = 'Model'
    #
    # def brand_name(self, obj):
    #     return obj.generation.model.brand.name
    #
    # brand_name.short_description = 'Brand'


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_group', 'padded_code', )
    list_filter = ('component_group__name', )
    search_fields = ['name', 'component_group__name', '=code']
    # inlines = [PartGroupInline, ]

    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(code=search_term_as_int)
        return queryset, may_have_duplicates

    def padded_code(self, obj):
        return str(obj.code).zfill(2)

    padded_code.short_description = 'Code'
    padded_code.admin_order_field = 'code'


@admin.register(PartGroup)
class PartGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ()
    search_fields = ['name', ]

    # def model_name(self, obj):
    #     return obj.component.component_group.generation.model.name
    #
    # model_name.short_description = 'Model'
    # model_name.admin_order_field = 'component__component_group__generation__model__name'
    #
    # def brand_name(self, obj):
    #     return obj.component.component_group.generation.model.brand.name
    #
    # brand_name.short_description = 'Brand'
    # brand_name.admin_order_field = 'component__component_group__generation__model__brand__name'
    #
    # def generation_name(self, obj):
    #     return obj.component.component_group.generation.name
    #
    # generation_name.short_description = 'Generation'
    # generation_name.admin_order_field = 'component__component_group__generation__name'
    #
    # def component_group_name(self, obj):
    #     return obj.component.component_group.name
    #
    # component_group_name.short_description = 'Component Group'
    # component_group_name.admin_order_field = 'component__component_group__name'


@admin.register(Part)
class PartAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('part_name', 'part_code', 'sales_restriction', 'cost', 'order_quantity', 'availability',
                    'is_original',)
    list_filter = ('sales_restriction', 'is_original')
    search_fields = ['part_name', 'part_code', ]


@admin.register(M2MPartGroupToPart)
class M2MPartGroupToPartAdmin(admin.ModelAdmin):
    list_display = ('part_group',
                    'part',
                    'component_group',
                    'brand',
                    'model',
                    'generation',
                    'number',
                    'repair_quantity', )
    list_filter = ('model', 'generation')
    search_fields = ['part_group__name', 'part__part_name', 'number', 'part__part_code']
    form = CustomM2MPartGroupToPartAdminForm

    class Media:
        js = ('epc/js/filterM2MPartGroupToPartAdmin.js',)


@admin.register(PicComponentGroup)
class PicComponentGroupAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'generation', 'component_group', 'picture', )
    list_filter = ('brand', 'model', 'generation', 'component_group', )


@admin.register(PicPartGroup)
class PicPartGroupAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'generation', 'part_group', 'picture', )
    list_filter = ('brand', 'model', 'generation', )

    class Media:
        js = ('epc/js/filterPicPartGroupAdmin.js',)
