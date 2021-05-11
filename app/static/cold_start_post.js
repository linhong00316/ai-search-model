function cold_start_post() {
    // var pic = document.getElementById("select_pic").files[0];
    // // console.log("pic")
    // // console.log(pic)

    // var check = [];
    // //把所有被选中的复选框的值存入数组
    // $("input[name='favor']:checked").each(function (i) {
    //     check[i] = $(this).val();
    // });
    // console.log(check)
    console.log("cold start post");
    var formData = new FormData($('#cold_start_form')[0]);

    // formData.append('check', check);
    $.ajax(
        '/cold_start',
        {
            type: 'POST',
            // dataType: 'json',
            cache: false,
            processData: false,
            contentType: false,
            data: formData,
            success: function (data) {
                console.log("success");
                // console.log(data['info']);
                $('#result_1').empty();
                $('#result_2').empty();
                // $('#result_3').empty();
                $('#result_1').append(data['r1']);
                $('#result_2').append(data['r2']);
                // $('#result_3').append(data['r3']);
            },
            error: function (xhr, type) {
            }
        }
    )
}