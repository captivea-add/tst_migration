odoo.define('survey.translator.signature', function(require) {
    require('web.dom_ready');

    /*
     * This file is intended to add interactivity to survey forms rendered by
     * the website engine.
     */

    var the_form = $('.js_surveyform');

    if (!the_form.length) {
        return $.Deferred().reject("DOM doesn't contain '.js_surveyform'");
    }

    var $sign = $(".signature");
    if (!$sign.length){
        return;
    }

    $sign.jSignature();

    $('.signature')
        .mouseleave(function(event){
    // OLD $('.js_set_signature').click(function(event){
        var $elem = $(event.currentTarget),
            $parent = $elem.parents('.panel-signature'),
            $input = $parent.find("input");
        var datapair = $parent.find('.signature').jSignature("getData", "image");
        if($input && $input.length && datapair.length > 1){
            $input.attr('value',datapair[1]);
        }
        console.log(datapair);
    }).on('touchend', function(event){
        // OLD $('.js_set_signature').click(function(event){
        var $elem = $(event.currentTarget),
            $parent = $elem.parents('.panel-signature'),
            $input = $parent.find("input");
        var datapair = $parent.find('.signature').jSignature("getData", "image");
        if($input && $input.length && datapair.length > 1){
            $input.attr('value',datapair[1]);
            console.log('input ok');
        }
        console.log(datapair);
    });

    $('.js_reset_signature').click(function(event){
        var $elem = $(event.currentTarget),
            $parent = $elem.parents('.panel-signature'),
            $input = $parent.find("input");
        $parent.find('.signature').jSignature("reset");
        $input.attr('value', '');
    });
});
