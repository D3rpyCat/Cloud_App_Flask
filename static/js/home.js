$(function () {
    $('#form-all-managers').submit(function (e) {
        var formData = {
            'dept_no': $('select[name=dept_no]').val()
        };
        $.ajax({
            type: 'GET', // define the type of HTTP verb we want to use (POST for our form)
            url: '/test/', // the url where we want to POST
            data: formData, // our data object
            dataType: 'json', // what type of data do we expect back from the server
            encode: true
        })
        // using the done promise callback
        .done(function (data) {
            
            // log data to the console so we can see
            console.log(data);
            
            $('#all-managers-result').empty()
            data.employees_names.forEach(element => {
                $('#all-managers-result').append('<li>'+element.first_name+' '+element.last_name+'</li>')
            });                
        });
        e.preventDefault();
    });
});