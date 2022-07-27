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
                            generation_options.each(function () {
                                if ($(this).css('display') != 'none') {
                                    $(this).prop("selected", true);
                                    return false;
                                }
                            });
                        });
                    },
                    error: function (e) {
                        console.error(JSON.stringify(e));
                    },
                });
            });
            $("#id_model").val(1).change();
        }
    });
});
