function upload_pic_func() {
    var pic = document.getElementById("select_pic").files[0];
    // console.log("pic")
    // console.log(pic)
    var formData = new FormData($('#setting_form')[0]);
    formData.append('img', pic);
    $.ajax(
        '/',
        {
            type: 'POST',
            // dataType: 'json',
            cache: false,
            processData: false,
            contentType: false,
            data: formData,
            success: function (data) {
                console.log("success");
                $('#result_test').append(data);
            },
            error: function (xhr, type) {
            }
        }
    )
}