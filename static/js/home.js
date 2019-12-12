$(function () {
    $('#form-all-managers').submit(function (e) {
        var formData = {
            'dept_no': $('select[name=dept_no]').val()
        };
        $.ajax({
            type: 'GET', // define the type of HTTP verb we want to use (POST for our form)
            url: '/all_managers/', // the url where we want to POST
            data: formData, // our data object
            dataType: 'json', // what type of data do we expect back from the server
            encode: true,
            beforeSend: function () {
                $('#form-all-managers button').empty()
                $('#form-all-managers button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
            }
        })
            // using the done promise callback
            .done(function (data) {

                // log data to the console so we can see
                console.log(data);

                $('#all-managers-result').empty()
                data.employees_names.forEach(element => {
                    $('#all-managers-result').append('<li>' + element.first_name + ' ' + element.last_name + '</li>')
                });

                $('#form-all-managers button').remove('span')
                $('#form-all-managers button').text('Valider')
            });
        e.preventDefault();
    });

    $('#form-all-employees').submit(function (e) {
        var formData = {
            'dept_no2': $('select[name=dept_no2]').val(),
            'title': $('select[name=title]').val()
        };
        $.ajax({
            type: 'GET', // define the type of HTTP verb we want to use (POST for our form)
            url: '/all_employees/', // the url where we want to POST
            data: formData, // our data object
            dataType: 'json', // what type of data do we expect back from the server
            encode: true,
            beforeSend: function () {
                $('#all-employees-result').empty()
                $('#form-all-employees button').empty()
                $('#form-all-employees button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
            }
        })
            // using the done promise callback
            .done(function (data) {
                // log data to the console so we can see
                console.log(data);
                if (data.dept_employees_names.length > 0) {
                    data.dept_employees_names.forEach(element => {
                        $('#all-employees-result').append('<li>' + element.first_name + ' ' + element.last_name + '</li>')
                    });
                }
                else {
                    $('#all-employees-result').append('Pas de résultats')
                }

                $('#form-all-employees button').remove('span')
                $('#form-all-employees button').text('Valider')
            });
        e.preventDefault();
    });

    $('#form-all-salaries').submit(function (e) {
        var formData = {
            'emp_emp_no': $('input[name=emp_emp_no]').val()
        };
        $.ajax({
            type: 'GET', // define the type of HTTP verb we want to use (POST for our form)
            url: '/all_salaries/', // the url where we want to POST
            data: formData, // our data object
            dataType: 'json', // what type of data do we expect back from the server
            encode: true,
            beforeSend: function () {
                $('#form-all-salaries button').empty()
                $('#form-all-salaries button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                $('#all-salaries-result').empty()
            }
        })
            // using the done promise callback
            .done(function (data) {
                // log data to the console so we can see
                console.log(data);
                if (data.labels.length > 0 && data.values.length > 0) {
                    $('#all-salaries-result').append('<canvas id="all-salaries-bar-chart"></canvas>')
                    var barChartData = {
                        labels: data.labels,
                        datasets: [{
                            label: 'Salaires',
                            backgroundColor: randomColor({ hue: 'blue', luminosity: 'light' }),
                            borderWidth: 1,
                            data: data.values
                        }]
                    };
                    var ctx = document.getElementById('all-salaries-bar-chart').getContext('2d');
                    window.myBar = new Chart(ctx, {
                        type: 'bar',
                        data: barChartData,
                        options: {
                            responsive: true,
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Histogramme des salaires par période'
                            },
                            tooltips: {
                                mode: 'index',
                            }
                        }
                    });
                }
                else {
                    $('#all-salaries-result').append('Pas de résultats')
                }
                $('#form-all-salaries button').remove('span')
                $('#form-all-salaries button').text('Valider')
            });
        e.preventDefault();
    });

    $('#form-dept-titles').submit(function (e) {
        var formData = {
            'dept_no3': $('select[name=dept_no3]').val(),
            'from_date_year': $('input[name=from_date_year]').val(),
            'from_date_month': $('input[name=from_date_month]').val()
        };
        $.ajax({
            type: 'GET', // define the type of HTTP verb we want to use (POST for our form)
            url: '/dept_titles_date/', // the url where we want to POST
            data: formData, // our data object
            dataType: 'json', // what type of data do we expect back from the server
            encode: true,
            beforeSend: function () {
                $('#form-dept-titles button').empty()
                $('#form-dept-titles button').append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span><span class="sr-only">Loading...</span>')
                $('#dept-titles-result').empty()
            }
        })
            // using the done promise callback
            .done(function (data) {
                // log data to the console so we can see
                console.log(data);
                if (data.labels.length > 0) {
                    $('#dept-titles-result').append('<canvas id="dept-titles-bar-chart"></canvas>')
                    var colors = randomColor({ count: 8, hue: 'blue', luminosity: 'light' })

                    var datasets = []
                    var count = 0
                    data.datasets.forEach(function (label) {
                        var data2 = []
                        for (var key in data.values) {
                            data.values[key].forEach(function (value) {
                                if (value.title == label) {
                                    data2.push(value.count)
                                }
                            })
                        }
                        var dataset = {
                            label: label,
                            backgroundColor: colors[count],
                            data: data2
                        }
                        count++
                        datasets.push(dataset)
                    })
                    var barChartData = {
                        labels: data.labels,
                        datasets: datasets
                    };
                    var ctx = document.getElementById('dept-titles-bar-chart').getContext('2d');
                    window.myBar = new Chart(ctx, {
                        type: 'bar',
                        data: barChartData,
                        options: {
                            title: {
                                display: true,
                                text: 'Histogramme empilé des titres des collaborateurs ayant intégré le département - ' + formData.from_date_year + '/' + formData.from_date_month
                            },
                            tooltips: {
                                mode: 'index',
                                intersect: false
                            },
                            responsive: true,
                            scales: {
                                xAxes: [{
                                    ticks: {
                                        autoSkip: true
                                    },
                                    stacked: true,
                                }],
                                yAxes: [{
                                    stacked: true
                                }]
                            }
                        }
                    });
                }
                else {
                    $('#dept-titles-result').append('Pas de résultats')
                }
                $('#form-dept-titles button').remove('span')
                $('#form-dept-titles button').text('Valider')
            });
        e.preventDefault();
    });

    $('#disconnect').on('click', function () {
        window.location.href='/logout/'
    });
});