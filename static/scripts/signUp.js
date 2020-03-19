$(document).ready(function() {
    console.log("hey hi");
    var but = $('#submitBut').click(function(event){
        event.preventDefault();
        var busCreds = $("#user_form_business input").toArray();
        var morCreds = $("#user_form_client input").toArray();
        busMail = busCreds[1].value.length != 0;
        busPass = busCreds[2].value.length != 0;
        morMail = morCreds[1].value.length != 0;
        morPass = morCreds[2].value.length != 0;
        validBus = busMail && busPass && !(morMail || morPass);
        validMor = morMail && morPass && !(busMail || busPass);
        //console.log(validBus);
        //console.log(validMor);
        if(validBus){
            $("#user_form_business #id_isOwner")[0].value = "True";
            $("#user_form_business").submit();
        } else if(validMor){
            $("#user_form_client #id_isOwner")[0].value = "False";
            $("#user_form_client").submit();
        } else {
            alert("Please enter a valid input.");
        }
    });
});