$(document).ready(function() {
    //Re-able for edit form
    if(! $(':input[name$=species]').val() == ""){
        $(':input[name=genes]').prop("disabled", false)
    } else {
        $(':input[name=genes]').prop("disabled", true)
    }
    $(':input[name$=species]').on('change', function() {
        $(':input[name=genes]').val(null).trigger('change');
        if ($(this).val() == ""){
            $(':input[name=genes]').prop("disabled", true)
        } else {
            $(':input[name=genes]').prop("disabled", false)
        }
    });
});

