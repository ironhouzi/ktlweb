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
File: Nivo Lightbox Setup
*/

$(window).load(function () {
    $('.nivoltbox').nivoLightbox({
        effect: 'fade', // The effect to use when showing the lightbox
        theme: 'default', // The lightbox theme to use
        keyboardNav: true, // Enable/Disable keyboard navigation (left/right/escape)
        onInit: function () {}, // Callback when lightbox has loaded
        beforeShowLightbox: function () {}, // Callback before the lightbox is shown
        afterShowLightbox: function (lightbox) {}, // Callback after the lightbox is shown
        beforeHideLightbox: function () {}, // Callback before the lightbox is hidden
        afterHideLightbox: function () {}, // Callback after the lightbox is hidden
        onPrev: function (element) {}, // Callback when the lightbox gallery goes to previous item
        onNext: function (element) {}, // Callback when the lightbox gallery goes to next item
        errorMessage: 'The requested content cannot be loaded. Please try again later.' // Error message when content can't be loaded
    });
});