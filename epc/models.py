from django.db import models
from django.contrib.auth.models import User
from time import time
from smart_selects.db_fields import ChainedForeignKey


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/ID_<user_id>_<username>/<filename>
    return 'ID_{0}_{1}/{2}'.format(instance.user.id, instance.user.username.lower(), filename.lower())


# ДЛЯ ЕБАНОГО ДЖАНГО make migrations // НИГДЕ НЕ ИСПОЛЬЗУЕТСЯ
def component_group_directory_path(instance, filename):
    pass


# ДЛЯ ЕБАНОГО ДЖАНГО make migrations // НИГДЕ НЕ ИСПОЛЬЗУЕТСЯ
def part_group_directory_path(instance, filename):
    pass


def pic_component_group_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<brand>/<model>/<generation>/component_group/<filename>
    return '{0}/{1}/{2}/pic_component_group/{3}'.format(instance.generation.model.brand.name.lower(),
                                                        instance.generation.model.name.lower(),
                                                        instance.generation.name.lower(),
                                                        filename.lower())


def pic_part_group_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<brand>/<model>/<generation>/part_group/<component>/<filename>
    return '{0}/{1}/{2}/pic_part_group/{3}/{4}'.format(instance.brand.name.lower(),
                                                       instance.model.name.lower(),
                                                       instance.generation.name.lower(),
                                                       instance.part_group.component.name.lower().replace(',', ''),
                                                       filename.lower())


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(default='default_avatar.png', upload_to=user_directory_path)
#
#     def __str__(self):
#         return f'{self.user.username}'
#
#

class RestorePasswordSessions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash_slice = models.CharField(max_length=16, null=False, blank=False)
    time_of_request = models.IntegerField(default=int(time()), null=False, blank=False)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')

    def __str__(self):
        return self.user

    class Meta:
        db_table = 'restore_password_session'


class Brand(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False, unique=True)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'brand'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'


class Model(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False, unique=True)
    brand = models.ForeignKey(Brand, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'model'
        verbose_name = 'Model'
        verbose_name_plural = 'Models'

    @property
    def spaceless_name(self):
        return self.name.replace(' ', '-').lower()

    @property
    def url_code(self):
        return self.name.split(' ')[1].lower()

    @property
    def minimal_picture_path(self):
        return 'templates/welcome/{0}.png'.format(self.name.replace(' ', '_').upper())


class Generation(models.Model):
    name = models.CharField(max_length=32, null=False, blank=False)
    model = models.ForeignKey(Model, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'generation'
        verbose_name = 'Generation'
        verbose_name_plural = 'Generations'
        # constraints = [
        #     models.UniqueConstraint(fields=['app_uuid', 'version_code'], name='unique appversion')
        # ]

    @property
    def code(self):
        return self.name.split(' ')[0]


class ComponentGroup(models.Model):
    code = models.PositiveSmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    # generation = models.ForeignKey(Generation, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.name)
        # if self.cg_code_name.code is not None:
        #     return self.generation.model.name + ' ' + self.generation.name + ' // ' + \
        #            str(self.cg_code_name.code) + ' - ' + self.cg_code_name.name
        # else:
        #     return self.generation.model.name + ' ' + self.generation.name + ' // ' + self.cg_code_name.name

    class Meta:
        db_table = 'component_group'
        verbose_name = 'Component Group'
        verbose_name_plural = 'Component Groups'


class Component(models.Model):
    code = models.PositiveSmallIntegerField(null=False, blank=False)
    name = models.CharField(max_length=64, null=False, blank=False)
    component_group = models.ForeignKey(ComponentGroup, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}{1} - {2}'.format(self.component_group.code, str(self.code).zfill(2), self.name)
        # if self.component_group.cg_code_name.code is not None and self.code is not None:
        #     return self.component_group.generation.model.name + ' ' + self.component_group.generation.name + ' // ' +
        #            str(self.component_group.cg_code_name.code) + str(self.code) + ' - ' + self.name
        # else:
        #     return self.component_group.generation.model.name + ' ' + self.component_group.generation.name + ' // ' +
        #            self.name

    class Meta:
        db_table = 'component'
        verbose_name = 'Component'
        verbose_name_plural = 'Components'

    @property
    def url_code(self):
        return "{0}{1}".format(str(self.component_group.code).zfill(2), str(self.code).zfill(2))


class PartGroup(models.Model):
    name = models.CharField(max_length=84, null=False, blank=False)
    # component = models.ForeignKey(Component, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'part_group'
        verbose_name = 'Part Group'
        verbose_name_plural = 'Part Groups'


class Part(models.Model):

    over_the_counter = 0
    tesla_only = 1
    restricted = 2
    e_procurement = 3
    not_for_resale = 4
    unrestricted = 5

    sales_restriction_choices = [
        (over_the_counter, 'Over-the-Counter(No VIN)'),
        (tesla_only, 'Tesla Only'),
        (restricted, 'Restricted'),
        (e_procurement, 'E-Procurement'),
        (not_for_resale, 'Not for Resale'),
        (unrestricted, 'Unrestricted(VIN)')
    ]

    part_name = models.CharField(max_length=634, null=False, blank=False)
    part_code = models.CharField(max_length=64, null=False, blank=False)
    sales_restriction = models.PositiveSmallIntegerField(choices=sales_restriction_choices, default=over_the_counter,
                                                         null=False, blank=False)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    order_quantity = models.PositiveSmallIntegerField(null=False, blank=False)
    availability = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_original = models.BooleanField(default=True)

    def __str__(self):
        return self.part_code

    class Meta:
        db_table = 'part'
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'


class M2MPartGroupToPart(models.Model):
    brand = models.ForeignKey(Brand, null=False, blank=False, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, null=False, blank=False, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, null=False, blank=False, on_delete=models.CASCADE)
    component_group = models.ForeignKey(ComponentGroup, null=False, blank=False, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, null=False, blank=False, on_delete=models.CASCADE)
    part_group = models.ForeignKey(PartGroup, null=False, blank=False, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, null=False, blank=False, on_delete=models.CASCADE)

    number = models.CharField(max_length=10, null=False, blank=False)
    info = models.CharField(max_length=1024, null=True, blank=True)
    repair_quantity = models.PositiveSmallIntegerField(null=False, blank=False)

    def __str__(self):
        return self.part_group.name

    class Meta:
        db_table = 'm2m_part_group_to_part'
        verbose_name = '(M2M) Part Group to Part'
        verbose_name_plural = '(M2M) Part Groups to Parts'


class PicComponentGroup(models.Model):
    brand = models.ForeignKey(Brand, null=False, blank=False, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, null=False, blank=False, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, null=False, blank=False, on_delete=models.CASCADE)
    component_group = models.ForeignKey(ComponentGroup, null=False, blank=False, on_delete=models.CASCADE)
    picture = models.ImageField(default='defaults/component_group_default.png',
                                upload_to=pic_component_group_directory_path)

    class Meta:
        db_table = 'pic_component_group'
        verbose_name = 'Picture (Component Group)'
        verbose_name_plural = 'Pictures (Component Group)'


class PicPartGroup(models.Model):
    brand = models.ForeignKey(Brand, null=False, blank=False, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, null=False, blank=False, on_delete=models.CASCADE)
    generation = models.ForeignKey(Generation, null=False, blank=False, on_delete=models.CASCADE)
    # model = ChainedForeignKey(Model, chained_field="brand", chained_model_field="brand",
    #                           null=False, blank=False, show_all=True, auto_choose=True)
    # generation = ChainedForeignKey(Generation, chained_field="model", chained_model_field="model",
    #                                null=False, blank=False, show_all=True, auto_choose=True)
    component_group = models.ForeignKey(ComponentGroup, null=False, blank=False, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, null=False, blank=False, on_delete=models.CASCADE)
    part_group = models.ForeignKey(PartGroup, null=False, blank=False, on_delete=models.CASCADE)
    picture = models.FileField(default='defaults/part_group_default.png',
                               upload_to=pic_part_group_directory_path,
                               max_length=500)

    class Meta:
        db_table = 'pic_part_group'
        verbose_name = 'Picture (Part Group)'
        verbose_name_plural = 'Pictures (Part Group)'
