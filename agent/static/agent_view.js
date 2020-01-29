jQuery.ajaxSettings.traditional = true;


$(document).ready(function () {

    populate_jobs();
    setInterval(populate_jobs,5000);
    get_connectivity();

    $("form#job_form").submit(function(e) {
        e.preventDefault();
        var formData = new FormData(this);


        $.ajax({
            url: '/execute',
            type: 'POST',
            data: formData,
            success: function (data) {
                entry = {
                    'executable': data['payload'],
                    'id': data['id'],
                    'agent': data['agent'],
                    'start': data['submission_time'],
                    'end': '-',
                    'status': 'submitted'
                }
                classColor = 'orange';

                $('#jobs_table').append('<tr><td>'+entry['executable']+'</td><td>'+entry['id']+'</td><td>'+entry['agent']+'</td><td>'+entry['start']+'</td><td>'+entry['end']+'</td><td><div href="/" class="ui '+classColor+' label">'+entry['status']+'</div></td></tr>');
            },
            cache: false,
            contentType: false,
            processData: false
        });
    });
});


function get_connectivity(){
    $.getJSON('/connectivity',{},function(connectivity){
        if(connectivity['status']=='connected'){
            classColor='green';
        }
        else{
            classColor='red';
        }

        $('#connectivity').html('<div class="ui '+classColor+' big label">'+connectivity['status']+'</div>')

    });

}

function populate_jobs(){
    $.getJSON('/jobs',{},function(jobs){
        $("#tbodyid").empty();
        $.each(jobs, function(i, job) {
            job = jobs[i]
            entry = {
                'executable': job['payload'],
                'id': job['id'],
                'agent': job['assigned_agent'],
                'start': job['submission_time'],
                'end': '-',
                'status': job['status']
            }
            if (entry['status']=='submitted'){
                classColor = 'orange';
            }
            else if (entry['status']=='completed'){
                classColor = 'green';
                entry['end']=job['completion_time']
            } else if (entry['status']=='Terminated'){
                classColor = 'red';
            }
            $('#jobs_table').append('<tr><td>'+entry['executable']+'</td><td>'+entry['id']+'</td><td>'+entry['agent']+'</td><td>'+entry['start']+'</td><td>'+entry['end']+'</td><td><a href="/get_report?id='+entry['id']+'" id="'+entry['id']+'"class="ui '+classColor+' label">'+entry['status']+'</a></td></tr>');
        });

    });
}
