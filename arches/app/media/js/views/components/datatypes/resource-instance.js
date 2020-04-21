define([
    'knockout',
    'underscore',
    'view-data',
    'arches',
    'views/components/widgets/resource-instance-select'
], function(ko, _, data, arches) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            this.resourceModels = [{
                graphid: null,
                name: ''
            }].concat(_.map(data.createableResources, function (graph) {
                return {
                    graphid: graph.graphid,
                    name: graph.name
                };
            }));
            if (!this.search) {
                this.isEditable = true;
                this.graphIsSemantic = !!params.graph.get('ontology_id');
                if (params.graph) {
                    var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId();});
                    if (cards.length) {
                        this.isEditable = cards[0].is_editable;
                    }
                } else if (params.widget) {
                    this.isEditable = params.widget.card.get('is_editable');
                }
                this.node = params;
                this.config = params.config;
                this.selectedResourceType = ko.observable('');
                this.selectedResourceType.subscribe(function(resourceType) {
                    if (resourceType.length > 0) {
                        resourceType = resourceType.concat(self.config.graphs());
                        self.config.graphs(resourceType);
                        self.selectedResourceType([]);
                    }
                });

                var preventSetup = false;
                var setupConfig = function(graph) {
                    var model = _.find(self.resourceModels, function(model){
                        return graph.graphid === model.graphid;
                    });
                    // use this so that graph.name won't get saved back to the node config
                    Object.defineProperty(graph, 'name', {
                        value: model.name
                    });
                    graph.ontologyProperty = ko.observable(ko.unwrap(graph.ontologyProperty));
                    graph.inverseOntologyProperty = ko.observable(ko.unwrap(graph.inverseOntologyProperty));
                    graph.editConfig = function(val) {
                        this.editing(val);
                    };
                    // use this so that graph.editing won't get saved back to the node config
                    Object.defineProperty(graph, 'editing', {
                        value: ko.observable(false),
                        enumerable: false,
                        writable: true
                    });

                    window.fetch(arches.urls.graph_nodes(graph.graphid))
                        .then(function(response){
                            if(response.ok) {
                                return response.json();
                            }
                            throw("error");
                        })
                        .then(function(json) {
                            var node = _.find(json, function(node) {
                                return node.istopnode;
                            });
                            // use this so that graph.ontologyclass won't get saved back to the node config
                            Object.defineProperty(graph, 'ontologyclass', {
                                value: node.ontologyclass
                            });
                        });

                    // need to listen to these properties change so we can 
                    // trigger a "dirty" state in the config
                    var triggerDirtyState = function() {
                        preventSetup = true;
                        self.config.graphs(self.config.graphs());
                        preventSetup = false;
                    };
                    graph.ontologyProperty.subscribe(triggerDirtyState);
                    graph.inverseOntologyProperty.subscribe(triggerDirtyState);

                    graph.removeRelationship = function(graph){
                        self.config.graphs.remove(graph);
                    };
                };

                this.config.graphs().forEach(function(graph) {
                    setupConfig(graph);
                });

                // this should only get completely run when discarding edits
                this.config.graphs.subscribe(function(graphs){
                    if (!preventSetup) {
                        graphs.forEach(function(graph) {
                            setupConfig(graph);
                        });
                    }
                });


                this.makeFriendly = function(item) {
                    if (!!item) {
                        var parts = item.split("/");
                        return parts[parts.length-1];
                    }
                    return '';
                };

                this.formatLabel = function(name, ontologyProperty, inverseOntologyProperty){
                    if (self.graphIsSemantic) {
                        return name + ' (' + self.makeFriendly(ontologyProperty) + '/' + self.makeFriendly(inverseOntologyProperty) + ')';
                    }
                    else {
                        return name;
                    }
                };

                this.getSelect2ConfigForOntologyProperties = function(value, domain, range) {
                    return {
                        value: value,
                        clickBubble: false,
                        placeholder: 'Select an Ontology Property',
                        closeOnSelect: true,
                        allowClear: false,
                        ajax: {
                            url: function() {
                                return arches.urls.ontology_properties;
                            },
                            data: function(term, page) {
                                var data = { 
                                    'domain_ontology_class': domain,
                                    'range_ontology_class': range,
                                    'ontologyid': ''
                                };
                                return data;
                            },
                            dataType: 'json',
                            quietMillis: 250,
                            results: function(data, page) {
                                return {
                                    results: data
                                };
                            }
                        },
                        id: function(item) {
                            return item;
                        },
                        formatResult: this.makeFriendly,
                        formatSelection: this.makeFriendly,
                        initSelection: function(el, callback) {
                            callback(value());
                        }
                    };
                };

            } else {
                var filter = params.filterValue();
                this.node = params.node;
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function() {
                    return {
                        op: self.op(),
                        val: self.searchValue() || ''
                    };
                }).extend({ throttle: 750 });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function(val) {
                    params.filterValue(val);
                });

            }
        },
        template: { require: 'text!datatype-config-templates/resource-instance' }
    });
    return name;
});
