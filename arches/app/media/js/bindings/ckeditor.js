define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
], function($, _, ko, arches) {
    /**
    * A knockout.js binding for the "ckeditor" rich text editor widget
    * - pass options to ckeditor using the following syntax in the knockout
    * data-bind attribute
    * @example
    * ckeditor: {height: 250}
    * @constructor
    * @name ckeditor
    */

    const initialize = function(element, valueAccessor, allBindings) {
        var modelValue = valueAccessor();
        var value = ko.utils.unwrapObservable(valueAccessor());
        const language = allBindings.get('language') || ko.observable(arches.activeLanguage);
        const direction = allBindings.get('direction') || ko.observable(arches.activeLanguageDir);
        var $element = $(element);
        var options = {bodyId: 'ckeditor'};
        const languageList = [];
        
        for(const lang of Object.keys(arches.languages)){
            languageList.push(`${lang}:${arches.languages[lang]}`);
        }
        /* eslint-disable no-undef */
        CKEDITOR.config.language_list = languageList;
        CKEDITOR.config.language = language();
        CKEDITOR.config.contentsLangDirection = direction();
        CKEDITOR.config.editorplaceholder = 'fooo'

        direction.subscribe(newValue => {
            CKEDITOR.config.contentsLangDirection = newValue;
            CKEDITOR.replace('ckeditor', CKEDITOR.config);
        });

        language.subscribe(newValue => {
            CKEDITOR.config.language = newValue;
        });

        if (allBindings.has('ckeditorOptions')){
            var opts = allBindings.get('ckeditorOptions');
            options = (typeof opts === 'object') ? opts : {};
        }

        // Set initial value and create the CKEditor
        $element.html(value);
        var editor = $element.ckeditor(options).editor;

        allBindings()?.attr?.disabled?.subscribe(disabled => {
            if(CKEDITOR.currentInstance && disabled === true || disabled === false) {
                editor?.setReadOnly(disabled);
            }
        });

        // bind to change events and link it to the observable
        var onChange = function(e) {
            var self = this;

            if (ko.isWriteableObservable(self)) {
                var newValue = $(e.listenerData).val();
                if (!((self() === null || self() === "") && (newValue === null || newValue === ""))) {
                    self(newValue);
                }
            }
            return true;
        };
        editor.on('change', onChange, modelValue, element);
        editor.on('afterCommandExec', (event => {
            if(event.data.name == 'language'){
                language(event.data.commandData);
            }
        }), modelValue, element);

        modelValue.subscribe(function(value){
            var self = this;
            var $element = $(element);
            var newValue = ko.utils.unwrapObservable(valueAccessor());
            if (editor.getData() != newValue) {
                // remove the listener and then add back to prevent `setData`
                // from triggering the onChange event
                editor.removeListener('change', onChange );
                editor.setData(newValue);
                editor.on('change', onChange, modelValue, element);
            }
        }, this);

        // Handle disposal if KO removes an editor through template binding
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            editor.updateElement();
            editor.destroy();
        });
    };

    ko.bindingHandlers.ckeditor = {
        init: (element, valueAccessor, allBindings) => {
            window.jQuery = $;
            require(['ckeditor4', 'ckeditor-jquery'], () => {
                initialize(element, valueAccessor, allBindings);
            });
        }
    };

    return ko.bindingHandlers.ckeditor;
});