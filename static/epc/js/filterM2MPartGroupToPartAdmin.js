function getCookie(c_name) {
    if (document.cookie.length > 0) {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

jQuery(function ($) {
    $(document).ready(function () {
        let pathArray = window.location.pathname.split('/');

        if (pathArray[pathArray.length - 2] === 'add') {
            $.ajaxSetup({
                headers: {"X-CSRFToken": getCookie('csrftoken')}
            });

            $("#id_brand").val(1).change();

            $('#id_model').on('change', function () {
                let model = this;
                $.ajax({
                    url: "/ajax/get-generation-admin/",
                    type: "POST",
                    data: {
                        model: model.value,
                    },
                    success: function (result) {
                        let generation_options = $('#id_generation').find('option').hide();

                        let generation_response = JSON.parse(result);
                        $.each(generation_response, function (key, value) {

                            generation_options.filter(function () {
                                return parseInt($(this).val()) === value['pk'];
                            }).show();

                        });
                        generation_options.each(function () {
                            if ($(this).css('display') != 'none') {
                                $(this).prop("selected", true);
                                return false;
                            }
                        });
                    },
                    error: function (e) {
                        console.error(JSON.stringify(e));
                    },
                });
            });

            $("#id_model").val(1).change();

            $('#id_component_group').on('change', function () {
                let component_group = this;
                $.ajax({
                    url: "/ajax/get-component-admin/",
                    type: "POST",
                    data: {
                        component_group: component_group.value,
                    },
                    success: function (result) {
                        let component = $('#id_component');
                        let component_options = component.find('option').hide();

                        let component_response = JSON.parse(result);
                        $.each(component_response, function (key, value) {

                            component_options.filter(function () {
                                return parseInt($(this).val()) === value['pk'];
                            }).show();
                        });

                        component_options.each(function () {
                            if ($(this).css('display') != 'none') {
                                $(this).prop("selected", true).change();
                                return false;
                            }
                        });
                    },

                    error: function (e) {
                        console.error(JSON.stringify(e));
                    },
                });
            });

            $('#id_component').on('change', function () {
                let component = this;
                $.ajax({
                    url: "/ajax/get-part-group-admin/",
                    type: "POST",
                    data: {
                        component: component.value,
                    },
                    success: function (result) {
                        let part_group = $('#id_part_group');
                        let part_group_options = part_group.find('option').hide();

                        let part_group_response = JSON.parse(result);
                        $.each(part_group_response, function (key, value) {

                            part_group_options.filter(function () {
                                return parseInt($(this).val()) === value['pk'];
                            }).show();
                        });

                        part_group_options.each(function () {
                            if ($(this).css('display') != 'none') {
                                $(this).prop("selected", true).change();
                                return false;
                            }
                        });
                    },

                    error: function (e) {
                        console.error(JSON.stringify(e));
                    },
                });
            });

            let searchRequest = null;

            $('#id_part_filter').on('keydown', function () {
                if ($(this).val().length >= 3) {

                    if (searchRequest != null)
                        searchRequest.abort();
                    searchRequest = $.ajax({
                        type: "POST",
                        url: "/ajax/get-parts-admin/",
                        data: {
                            'code': $(this).val().trim()
                        },
                        dataType: "text",
                        success: function (msg) {

                            console.log(msg);
                            let query = JSON.parse(JSON.parse(msg));

                            let part = $('#id_part');
                            let part_options = part.find('option').hide();
                            query.forEach(part => {
                                let partId = part.id;
                                part_options.filter(function () {
                                    return parseInt($(this).val()) === partId;
                                }).show();

                            })

                            part_options.each(function () {
                                if ($(this).css('display') != 'none') {
                                    $(this).prop("selected", true).change();
                                    return false;
                                }
                            });
                        }
                    });
                }
            });
        }
    });
});
