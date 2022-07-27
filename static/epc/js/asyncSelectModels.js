function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1)
        {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }

jQuery(function($){
    $(document).ready(function() {
        let pathArray = window.location.pathname.split('/');
        if (pathArray[pathArray.length - 2] === 'add') {
            let models = document.getElementById("id_model");
            // models.options.length = 0;
            if ($('#id_brand > option').length === 1) {
                // TODO
            }
            $("#id_brand").change(function() {
                console.log( $(this).val() );
                $.ajaxSetup({
                    headers: { "X-CSRFToken": getCookie('csrftoken') }
                });
                $.ajax({
                    url:"/ajax/get_models/",
                    type:"POST",
                    data: {
                        brand: $(this).val(),
                    },
                    success: function(result) {
                        console.log(result);

                        models.options.length = 0;
                        // for (let k in result) {
                        //     models.options.add(new Option(k['fields']['name'], k['pk']));
                        // }
                        try {
                            $.each(JSON.parse(result), function (index, item) {
                                models.options.add(new Option(item['fields']['name'], item['pk']));
                            });
                        } catch (e) {

                        }

                    },
                    error: function(e) {
                        // console.error(JSON.stringify(e));
                    },
                });
            });
        }
    });
});