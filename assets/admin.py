from django.contrib import admin
from assets import models
# Register your models here.
from assets import asset_handler
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import widgets


class NewAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_type', 'sn', 'model', 'manufacturer', 'c_time', 'm_time']
    list_filter = ['asset_type', 'manufacturer', 'c_time']
    search_fields = ('sn',)

    actions = ['approve_selected_assets']

    def approve_selected_assets(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        success_upline_number = 0
        for asset_id in selected:
            obj = asset_handler.ApproveAsset(request, asset_id)
            ret = obj.asset_upline()
            if ret:
                success_upline_number += 1

        self.message_user(request, "成功批准  %s  条新资产上线！" % success_upline_number)

    approve_selected_assets.short_description = '批准新资产上线'


class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_type', 'name', 'status', 'approved_by', 'c_time', 'm_time']


"""新增功能测试"""


class DownloadFileWidget(widgets.AdminFileWidget):
    id = None
    template_name = 'assets/download_file_input.html'

    def __init__(self, id, attrs=None):
        self.id = id
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        print(self, name, value, attrs, self.id)
        context['download_url'] = reverse('attachment', kwargs={'pk': self.id})
        return context


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', '_get_download_url']
    search_fields = ['name']
    my_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.my_id_for_formfield = obj.id
        return super(AttachmentAdmin, self).get_form(request, obj=obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if self.my_id_for_formfield:
            if db_field.name == 'file':
                kwargs['widget'] = DownloadFileWidget(id=self.my_id_for_formfield)

        return super(AttachmentAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def _get_download_url(self, instance):
        return format_html('<a href="{}">{}</a>', reverse('attachment', kwargs={'pk': instance.id}), instance.name)

    _get_download_url.short_description = 'download'


admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Server)
admin.site.register(models.StorageDevice)
admin.site.register(models.SecurityDevice)
admin.site.register(models.NetworkDevice)
admin.site.register(models.Software)
admin.site.register(models.BusinessUnit)
admin.site.register(models.Contract)
admin.site.register(models.Tag)
admin.site.register(models.IDC)
admin.site.register(models.Manufacturer)
admin.site.register(models.CPU)
admin.site.register(models.Disk)
admin.site.register(models.NIC)
admin.site.register(models.RAM)
admin.site.register(models.EventLog)
admin.site.register(models.NewAssetApprovalZone, NewAssetAdmin)
admin.site.register(models.AllProjects)
admin.site.register(models.Attachment, AttachmentAdmin)
