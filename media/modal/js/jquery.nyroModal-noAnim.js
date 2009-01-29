/*
 * nyroModal - jQuery Plugin
 * http://nyromodal.nyrodev.com
 *
 * Copyright (c) 2008 Cedric Nirousset (nyrodev.com)
 * Licensed under the MIT license
 *
 * Include this file AFTER nyroModal if you want absolutely no animation with nyroModal
 *
 * $Date: 2008-11-29 (Sat, 29 Nov 2008) $
 * $version: 1.3.1
 */
 jQuery(function($) {
	$.fn.nyroModal.settings.showBackground = function(elts, settings, callback) {
		elts.bg.css({opacity:0.75});
		callback();
	};
	
	$.fn.nyroModal.settings.hideBackground = function(elts, settings, callback) {
		elts.bg.hide();
		callback();
	};
	
	$.fn.nyroModal.settings.showContent = function(elts, settings, callback) {
		elts.contentWrapper
			.css({
				width: settings.width+'px',
				marginLeft: (settings.marginLeft)+'px',
				height: settings.height+'px',
				marginTop: (settings.marginTop)+'px'
			})
			.show()
		callback();
	};
	
	$.fn.nyroModal.settings.hideContent = function(elts, settings, callback) {
		elts.contentWrapper.hide();
		callback();
	};
	
	$.fn.nyroModal.settings.showLoading = function(elts, settings, callback) {
		elts.loading
			.css({
				marginTop: settings.marginTopLoading+'px',
				marginLeft: settings.marginLeftLoading+'px'
			})
			.show();
		callback();
	};
	
	$.fn.nyroModal.settings.hideLoading = function(elts, settings, callback) {
		elts.loading.hide();
		callback();
	};
	
	$.fn.nyroModal.settings.showTransition = function(elts, settings, callback) {
		// Put the loading with the same dimensions of the current content
		elts.loading
			.css({
				marginTop: elts.contentWrapper.css('marginTop'),
				marginLeft: elts.contentWrapper.css('marginLeft'),
				height: elts.contentWrapper.css('height'),
				width: elts.contentWrapper.css('width')
			})
			.show();
		elts.contentWrapper.hide();
		callback();
	};
	
	$.fn.nyroModal.settings.hideTransition = function(elts, settings, callback) {
		// Place the content wrapper underneath the the loading with the right dimensions
		elts.contentWrapper
			.css({
				width: settings.width+'px',
				marginLeft: settings.marginLeft+'px',
				height: settings.height+'px',
				marginTop: settings.marginTop+'px'
			})
			.show();
		elts.loading.hide();
		callback();
	};
	
	$.fn.nyroModal.settings.resize = function(elts, settings, callback) {
		elts.contentWrapper
			.css({
				width: settings.width+'px',
				marginLeft: settings.marginLeft+'px',
				height: settings.height+'px',
				marginTop: settings.marginTop+'px'
			});
		callback();
	};
	
	$.fn.nyroModal.settings.updateBgColor = function(elts, settings, callback) {
		elts.bg.css({backgroundColor: settings.bgColor});
		callback();
	};
});