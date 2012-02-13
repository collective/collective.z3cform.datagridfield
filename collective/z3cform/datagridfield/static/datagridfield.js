dataGridField2Functions = new Object();

jQuery(function($) {

    dataGridField2Functions.getInputOrSelect = function(node) {
        /* Get the (first) input or select form element under the given node */
        
        var inputs = node.getElementsByTagName("input");
        if(inputs.length > 0) {
            return inputs[0];
        }
        
        var selects = node.getElementsByTagName("select");
        if(selects.length > 0) {
            return selects[0];
        }

        return null;
    }

    dataGridField2Functions.getWidgetRows = function(currnode) {
        /* Return primary nodes with class of datagridwidget-row,
           they can be any tag: tr, div, etc. */
        tbody = this.getParentByClass(currnode, "datagridwidget-body");
        return this.getRows(tbody);
    }

    dataGridField2Functions.getRows = function(tbody) {
        /* Return primary nodes with class of datagridwidget-row,
           they can be any tag: tr, div, etc. */
        
        var rows = new Array()
        
        rows = $(tbody).find('.datagridwidget-row');
                      
        return rows;   
    } 

    dataGridField2Functions.autoInsertRow = function(e) {
        /* Add a new row when changing the last row 
           (i.e. the infamous auto insert feature)
        
         */
        var currnode = window.event ? window.event.srcElement : e.currentTarget;

        // fetch required data structure   
        var tbody = dataGridField2Functions.getParentByClass(currnode, "datagridwidget-body");
        var thisRow = dataGridField2Functions.getParentRow(currnode);

        // Remove the auto-append functionality from the row
        $('.auto-append > .datagridwidget-cell').unbind('change');
        $(thisRow).removeClass('auto-append');
        
        // Create a new row
        var newtr = dataGridField2Functions.createNewRow(thisRow);
        // Add auto-append functionality to our new row
        $(newtr).addClass('auto-append');
                                                            
        /* Put new row to DOM tree after our current row.  Do this before 
         * reindexing to ensure that any Javascript we insert that depends on 
         * DOM element IDs (such as plone.formwidget.autocomplete) will
         * pick up this row before any IDs get changed.  At this point, 
         * we techinically have duplicate TT IDs in our document
         * (one for this new row, one for the hidden row), but jQuery 
         * selectors will pick up elements in this new row first.
         */
        $(newtr).insertAfter(thisRow);
        $('.auto-append > .datagridwidget-cell').change(dataGridField2Functions.autoInsertRow);

        dataGridField2Functions.reindexRow(tbody, newtr, 'AA'); 
        
        // Update order index to give rows correct values
        dataGridField2Functions.updateOrderIndex(tbody,true);
    }

    dataGridField2Functions.addRowAfter = function(currnode) {
        /*
            Creates a new row after the clicked row
        */
        
        // fetch required data structure
        var tbody = this.getParentByClass(currnode, "datagridwidget-body"); 
        var thisRow = this.getParentRow(currnode); 

        var newtr = this.createNewRow(thisRow);
        if (thisRow.hasClass('auto-append') == true) {
            $(newtr).insertBefore(thisRow);
        } else {
            $(newtr).insertAfter(thisRow);
        }
        
        // update orderindex hidden fields
        this.updateOrderIndex(tbody,true);
      
    }

    dataGridField2Functions.createNewRow = function(node) { 
        /* Creates a new row 
               
           @param node A row in a table where we'll be adding the new row
        */
        var tbody = this.getParentByClass(node, "datagridwidget-body");   
        
        // hidden template row 
        var emptyRow = $(tbody).find('.datagridwidget-empty-row');
        
        var markup = $(emptyRow).clone(true);
        
        var newTr = $(markup).attr("class","datagridwidget-row");
        
        return newTr[0]
    }    


    dataGridField2Functions.removeFieldRow = function(node) {
        /* Remove the row in which the given node is found */
        var tbody = this.getParentByClass(node, "datagridwidget-body"); 
        var row = this.getParentRow(node);
        $(row).remove();
        this.updateOrderIndex(tbody,false);
    }
    
    dataGridField2Functions.moveRow = function(currnode, direction){
        /* Move the given row down one */
               
        var tbody = this.getParentByClass(currnode, "datagridwidget-body");    
        
        var rows = this.getWidgetRows(currnode);
        
        var row = this.getParentRow(currnode);      
        if(row == null) {
            alert("Couldn't find DataGridWidget row");
            return;
        }
        
        var idx = null;
        
        // We can't use nextSibling because of blank text nodes in some browsers
        // Need to find the index of the row
        
        rows.each(function (i) {
            if (this == row[0]) {
                idx = i;
            }
        });

        // Abort if the current row wasn't found
        if(idx == null)
            return;
                
            
        // The up and down should cycle through the rows, excluding the auto-append and 
        // empty-row rows.
        var validrows = 0;
        rows.each(function (i) {
            if ($(this).hasClass('datagridwidget-empty-row') != true && $(this).hasClass('auto-append') != true) {
                validrows+=1;
            }
        });
        
        if (idx+1 == validrows) {
            if (direction == "down") {
                this.moveRowToTop(row);
            } else {
                nextRow = rows[idx-1];
                this.shiftRow(nextRow, row);
            }
            
        } else if (idx == 0) {
            if (direction == "up") {
                this.moveRowToBottom(row);
            } else {
                nextRow = rows[parseInt(idx+1)];
                this.shiftRow(row, nextRow);
            }
            
        } else {
            if (direction == "up") {
                nextRow = rows[idx-1];
                this.shiftRow(nextRow, row);
            } else {
                nextRow = rows[parseInt(idx+1)];
                this.shiftRow(row, nextRow);
            }
        }
        this.updateOrderIndex(tbody);
    }
    
    dataGridField2Functions.moveRowDown = function(currnode){
        this.moveRow(currnode, "down");
    }

    dataGridField2Functions.moveRowUp = function(currnode){
        this.moveRow(currnode, "up");
    }

    dataGridField2Functions.shiftRow = function(bottom, top){
        /* Put node top before node bottom */
        $(top).insertBefore(bottom);   
    }
    
    dataGridField2Functions.moveRowToTop = function (row) {
        rows = this.getWidgetRows(row);
        $(row).insertBefore(rows[0]);
    }
    
    dataGridField2Functions.moveRowToBottom = function (row) {
        rows = this.getWidgetRows(row);
        
        // make sure we insert the directly above any auto appended rows
        var insert_after = 0;
        rows.each(function (i) {
            if ($(this).hasClass('datagridwidget-empty-row') != true && $(this).hasClass('auto-append') != true) {
                insert_after = i;
            }
        });
        $(row).insertAfter(rows[insert_after]);
    }

    dataGridField2Functions.reindexRow = function (tbody, row, newindex) {
        var name_prefix = $(tbody).attr('data-name_prefix') + '.';
        var id_prefix = $(tbody).attr('data-id_prefix') + '-';

        $(row).find('[name^="' + name_prefix +'"]').each(function(){
            var oldname = this.name.substr(name_prefix.length);
            var oldindex1 = oldname.split('.', 1)[0];
            var oldindex2 = oldname.split('-', 1)[0];
            /* Name fields can have '-' for empty values */
            var oldindex = 0;
            if (oldindex1.length < oldindex2.length)
            {
                oldindex = oldindex1;
            } else {
                oldindex = oldindex2;
            }
            this.name = name_prefix + newindex + oldname.substr(oldindex.length);
        });
        $(row).find('[id*="' + id_prefix +'"]').each(function(){
            var regexp = new RegExp(id_prefix + ".*?-")
            this.id = this.id.replace(regexp, id_prefix + newindex + "-");
        });
        $(row).find('[for*="' + id_prefix +'"]').each(function(){
            var regexp = new RegExp(id_prefix + ".*?-")
            this.setAttribute('for', this.getAttribute('for').replace(regexp, id_prefix + newindex + "-"));
        });
        $(row).find('[class*="' + name_prefix +'"]').each(function(){
            var regexp = new RegExp(name_prefix + ".*?\\.")
            this.className = this.className.replace(regexp, name_prefix + newindex + ".");
        });
    }


    dataGridField2Functions.updateOrderIndex = function (tbody, backwards) {

        /* Split from the dataGridField2 approach here - and just re-do
         * the numbers produced by z3c.form
         */
        var name_prefix = $(tbody).attr('data-name_prefix') + '.';

        var rows = this.getRows(tbody); 
        for (var i=0; i<rows.length; i++) {
            var idx = backwards ? rows.length-i-1 : i;
            var row = rows[idx];
            if ($(row).hasClass('datagridwidget-empty-row') || $(row).hasClass('auto-append')) {
                continue
            }
            dataGridField2Functions.reindexRow(tbody, row, idx);
        }

        $(document).find('input[name="' + name_prefix + 'count"]').each(function(){
            // do not include the TT and the AA rows in the count
            var count = rows.length;
            if ($(rows[count-1]).hasClass('datagridwidget-empty-row')) {
                count--;
            }
            if ($(rows[count-1]).hasClass('auto-append')) {
                count--;
            }
            this.value = count;
        });
    }

    dataGridField2Functions.getParentElement = function(currnode, tagname) {
        /* Find the first parent node with the given tag name */

        tagname = tagname.toUpperCase();
        var parent = currnode.parentNode;

        while(parent.tagName.toUpperCase() != tagname) {
            parent = parent.parentNode;
            // Next line is a safety belt
            if(parent.tagName.toUpperCase() == "BODY") 
                return null;
        }

        return parent;
    }
    
    dataGridField2Functions.getParentRow = function (node) {
        return this.getParentByClass(node, 'datagridwidget-row')
    }
    
    dataGridField2Functions.getParentByClass = function(node, klass) {
        var parent = $(node).closest("." + klass);
        
        if (parent.length) {
            return parent;
        }
        
        return null;
    }

    dataGridField2Functions.getParentElementById = function(currnode, id) {
        /* Find the first parent node with the given id 
        
            Id is partially matched: the beginning of
            an element id matches parameter id string.
        
            Currnode: Node where ascending in DOM tree beings
            Id: Id string to look for. 
                    
        */
        
        id = id.toLowerCase();
        var parent = currnode.parentNode;

        while(true) {
           
            var parentId = parent.getAttribute("id");
            if(parentId != null) {    	
                 if(parentId.toLowerCase().substring(0, id.length) == id) break;
            }
                
            parent = parent.parentNode;
            // Next line is a safety belt
            if(parent.tagName.toUpperCase() == "BODY") 
                return null;
        }

        return parent;
    }

    /* Bind the handlers to the auto append rows */
    $('.auto-append > .datagridwidget-cell').change(dataGridField2Functions.autoInsertRow);

});