$(document).ready(function(){

            //add this ddslick stuff to add images, then on select I update the value coz it bugs out?
            $('#recdados').ddslick({

                onSelected: function(data){
                    var str = data.selectedData.value
                    document.getElementById("recdado").value = str;
                }

            });
        });