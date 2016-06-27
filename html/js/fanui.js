function Dialog() {
    var d_container = $("<div/>", {
        "class": "dialog", "style": "display:none"
    });
    var d_header = $("<div/>", {
        "class": "dialog-header"
    });

    var d_body = $("<div/>", {
        "class": "dialog-body"
    });

    d_header.appendTo(d_container);
    d_body.appendTo(d_container);
    d_container.appendTo($("body"));
    d_container.hide();
    d_header.hide();
    d_body.hide();

    Dialog.prototype.setContent = function (html) {
        d_body.html(html);
    };

    Dialog.prototype.hide = function () {
        d_container.hide();
        d_header.hide();
        d_body.hide();
    };

    Dialog.prototype.show = function () {
        d_container.show();
        d_header.show();
        d_body.show();
        var body_click_count = 0;
        //body_click_count=1时不触发body.click事件，第二次触发;
        d_container.click(function () {
            body_click_count = body_click_count - 1 ;
            //console.log("dialog click")
        });
        $("body").click(function () {
            body_click_count = body_click_count + 1;
            //console.log("body_click_count: " + body_click_count);
            if (body_click_count % 2 === 0) {
                $("body").off('click');
                d_container.hide();
            }
        });
    };
    Dialog.prototype.setPosition = function (left, top) {
        d_header.css({"left": d_body.width()/2});
        d_body.css({"top": d_header.width()/2});
        var w_fix = 20;
        var gap = $(window).width() - d_body.width() - left - w_fix;
        if  (gap < 0)  {d_body.css({"left": gap });}else {d_body.css({"left": 0 });}
        d_container.css({"left": left, "top": top})
    };
    Dialog.prototype.width = function () {
        return d_body.width();
    };
    Dialog.prototype.height = function () {
        return d_header.height();
    };
}

Dialog.getSingleton = function()  {
    if (typeof Dialog.singleton === 'undefined'){
        Dialog.singleton = new Dialog();
    }
    return Dialog.singleton;
};


$(".sidebar dt").css({"background-color":"#3992d0"});
$(".sidebar dt img").attr("src","images/left/select_xl01.png");

$(function(){
    $(".sidebar dd").hide();
    $(".sidebar dt").click(function(){
        $(".sidebar dt").css({"background-color":"#3992d0"});
        $(this).css({"background-color": "#317eb4"});
        $(this).parent().find('dd').removeClass("menu_choice");
        $(".sidebar dt img").attr("src","images/left/select_xl01.png");
        $(this).parent().find('img').attr("src","images/left/select_xl.png");
        $(".menu_choice").slideUp();
        $(this).parent().find('dd').slideToggle();
        $(this).parent().find('dd').addClass("menu_choice");
    });
});