
$(document).ready(function(){
    var form = $("#form_buying_product");
    console.log(form);

    function basketUpdating(product_id, nmb, is_delete=true){
    var data = {};
        data.product_id = product_id;
        data.nmb = nmb;
        var csrf_token = $('#form_buying_product [name="csrfmiddlewaretoken"]').val();
        data["csrfmiddlewaretoken"] = csrf_token;

        if (is_delete){
            data["is_delete"] = true;
        }

        var url = form.attr("action");

        console.log(data);

            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                cache: true,
                success: function (data) {
                    console.log("OK");
                    console.log(data.products_total_nmb);
                    if (data.products_total_nmb || data.products_total_nmb == 0) {
                        $('#basket_total_nmb').text("("+data.products_total_nmb+")");
                        console.log(data.products);
                        $('.basket-items ul').html("");
                        $.each(data.products, function(k, v){
                            $('.basket-items ul').append('<li>'+v.name+' x ' + v.nmb + ' шт. ' + 'по ' + v.price_per_item + ' грн.  ' +
                                '<a class="delete-items" href="" data-product_id="'+v.id+'">x</a>' +
                            '</li>');
                })
                    }

                },
                error: function(){
                    console.log("error");
                }
            })
    }


    form.on("submit", function(e){
    e.preventDefault();
    console.log("123");
    var nmb = $("#number").val();
    console.log(nmb);
    var submit_btn = $("#submit_btn");
    var product_id = submit_btn.data("product_id");
    var product_name = submit_btn.data("name");
    var product_price = submit_btn.data("price");
    console.log(product_id);
    console.log(product_name);
    console.log(product_price);

    basketUpdating(product_id, nmb, is_delete=false)

    });



    function showingBasket(){
        $(".basket-items").removeClass("hidden");
    };

//    $(".basket-container").on("click", function(e){
//        e.preventDefault();
//        showingBasket();
//    });

    $(".basket-container").mouseover(function(){
        showingBasket();
    });

//    $(".basket-container").mouseout(function(){
//        showingBasket();
//    });

    $(document).on('click', 'delete-items', function(e){
        e.preventDefault();
        product_id = $(this).data("product_id");
        nmb = 0;
        basketUpdating(product_id, nmb, is_delete=true);
        $(this).closest('li').remove();
    });

    function calculatingBasketAmount(){
        var total_order_amount = 0;
        $('.total-product-in-basket-amount').each(function(){
         console.log($(this).text());
         total_order_amount += parseFloat($(this).text());
         });
         $('#total-order-amount').text(total_order_amount.toFixed(2));
    };

    $(document).on('change', ".product-in-basket-nmb", function(){
        var current_nmb = $(this).val();
        var current_tr = $(this).closest('tr');
        var current_price = parseFloat(current_tr.find('.product-price').text()).toFixed(2);
        var total_amount = parseFloat(current_nmb*current_price).toFixed(2);
        current_tr.find('.total-product-in-basket-amount').text(total_amount);

        calculatingBasketAmount();
    });
        calculatingBasketAmount();

});
