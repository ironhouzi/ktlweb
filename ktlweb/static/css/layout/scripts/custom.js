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
File: Custom JS
*/

// Images
// Remove width and height from images that have it in their HTML code
// this ensures that images stay responsive
jQuery(document).ready(function ($) {
    $('img').removeAttr('width height');
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Alert Messages
$(".alert-msg .close").click(function () {
    $(this).parent().animate({
        "opacity": "0"
    }, 400).slideUp(400);
    return false;
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Accordions
$(".accordion-title").click(function () {
    $(".accordion-title").removeClass("active");
    $(".accordion-content").slideUp("normal");
    if ($(this).next().is(":hidden") == true) {
        $(this).addClass("active");
        $(this).next().slideDown("normal");
    }
});
$(".accordion-content").hide();

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Toggles
$(".toggle-title").click(function () {
    $(this).toggleClass("active").next().slideToggle("fast");
    return false;
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Tabs
$(".tab-wrapper").tabs({
    event: "click"
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// FitVids - Media Such as Vimeo, Youtube etc.
$(".mediabox").fitVids();

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Show / Hide Topbar
$("#slideit").click(function () {
    $("#slidepanel").slideDown("slow");
});
$("#closeit").click(function () {
    $("#slidepanel").slideUp("slow");
});
// Switch buttons from "+" to "-" on click
$("#openpanel a").click(function () {
    $("#openpanel a").toggle();
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Scroll to top Button
jQuery("#scrolltotop").click(function () {
    jQuery("body,html").animate({
        scrollTop: 0
    }, 600);
});

jQuery(window).scroll(function () {
    if (jQuery(window).scrollTop() > 150) {
        jQuery("#scrolltotop").addClass("visible");
    } else {
        jQuery("#scrolltotop").removeClass("visible");
    }
});

// ###########################################################################
// ###########################################################################
// ###########################################################################
// Mobile Menu based on:
// "Convert a Menu to a Dropdown for Small Screens" from Chris Collier - http://css-tricks.com/convert-menu-to-dropdown/
// "Submenu's with a dash" Daryn St. Pierre - http://jsfiddle.net/bloqhead/Kq43X/

// Create the dropdown base
$('<form id="mobilemenu"><select /></form>').appendTo("#topnav");
// Create default option "Go to..." or something else
$("<option />", {
    "selected": "selected",
    "value": "",
    "text": "MENU"
}).appendTo("#topnav select");
// Populate dropdown with menu items
$("#topnav a").each(function () {
    var el = $(this);
    // Modified here to add puffer to menu items depending on which level they are
    if ($(el).parents(".sub-menu .sub-menu .sub-menu").length >= 1) {
        $('<option />', {
            'value': el.attr("href"),
            'text': '- - - ' + el.text()
        }).appendTo("#topnav select");
    } else if ($(el).parents(".sub-menu .sub-menu").length >= 1) {
        $('<option />', {
            'value': el.attr("href"),
            'text': '- - ' + el.text()
        }).appendTo("#topnav select");
    } else if ($(el).parents(".sub-menu").length >= 1) {
        $('<option />', {
            'value': el.attr("href"),
            'text': '- ' + el.text()
        }).appendTo("#topnav select");
    } else {
        $('<option />', {
            'value': el.attr("href"),
            'text': el.text()
        }).appendTo("#topnav select");
    }
});
// Make the dropdown menu actually work
$("#topnav select").change(function () {
    if ($(this).find('option:selected').val() !== '#') {
        window.location = $(this).find('option:selected').val();
    }
});
// End Mobile Menu