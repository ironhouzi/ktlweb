/*
Template Name: Book Of Wisdom
Template URI: http://www.os-templates.com/
Description: Designed and Built by <a href="http://www.os-templates.com/">OS Templates</a>. This modern template is adaptable, lightweight and fully customisable. The template is easy to use, enabling you to create your site within minutes.
Version: 1.0.1
Author: OS-Templates.com
Author URI: http://www.os-templates.com/
Copyright: OS-Templates.com
Licence: Single Site
Licence URI: http://www.os-templates.com/template-terms
File: Flexslider Setup JS
*/


// Flexslider - Homepage Slider
$(".flex-homepage").flexslider({
    selector: ".flex-slides > li",
    animation: "fade",
    touch: true,
    animationLoop: true,
    directionNav: true,
    controlNav: false,
    pauseOnHover: true,
    prevText: "<em>Previous<\/em>",
    nextText: "<em>Next<\/em>",
    smoothHeight: true
});

// Flexslider - Carousels
$(".flex-carousel").flexslider({
    selector: ".flex-slides > li",
    animation: "slide",
    touch: true,
    directionNav: true,
    controlNav: false,
    pauseOnHover: true,
    prevText: "<em>Previous<\/em>",
    nextText: "<em>Next<\/em>",
    itemWidth: 222,
    itemMargin: 30, // Margin must also be set the same in the CSS file
    move: 1
});

// Flexslider - Standard Slider With Everything
$(".flex-full-basic").flexslider({
    selector: ".flex-slides > li",
    animation: "slide",
    touch: true,
    animationLoop: true,
    directionNav: true,
    controlNav: true,
    pauseOnHover: true,
    prevText: "<em>Previous<\/em>",
    nextText: "<em>Next<\/em>",
    smoothHeight: true
});

// Flexslider - Standard Slider With Thumbs
$(".flex-thumbs").flexslider({
    selector: ".flex-slides > li",
    animation: "slide",
    touch: true,
    animationLoop: true,
    directionNav: false,
    controlNav: "thumbnails",
    pauseOnHover: true,
    smoothHeight: true
});

// Flexslider - Horizontal Text Slider
$(".flex-text-horizontal").flexslider({
    selector: ".flex-slides > li",
    animation: "slide",
    touch: true,
    animationLoop: true,
    directionNav: false,
    controlNav: false,
    direction: "horizontal",
    pauseOnHover: true,
    smoothHeight: true
});

// Flexslider - Vertical Text Slider
$(".flex-text-vertical").flexslider({
    selector: ".flex-slides > li",
    animation: "slide",
    touch: true,
    animationLoop: true,
    directionNav: false,
    controlNav: false,
    direction: "vertical",
    pauseOnHover: true,
    smoothHeight: true
});