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
        $(function () {
            $.ajaxSetup({
                headers: { "X-CSRFToken": getCookie('csrftoken') }
            });
        });
        $("#id_brand").change(function() {
            console.log( $(this).val() );
            $.ajax({
                url:"/ajax/get_models/",
                type:"POST",
                data: {
                    brand: $(this).val(),
                },
                success: function(result) {
                    console.log(result);
                    let models = document.getElementById("id_model");
                    models.options.length = 0;
                    for (let k in result) {
                        models.options.add(new Option(k, result[k]));
                    }
                },
                error: function(e){
                    // console.error(JSON.stringify(e));
                },
            });
        });
    });
});