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
                $('#result_1').empty();
                $('#result_2').empty();
                $('#result_3').empty();
                $('#result_1').append(data['r1']);
                $('#result_2').append(data['r2']);
                $('#result_3').append(data['r3']);
            },
            error: function (xhr, type) {
            }
        }
    )
}