/*global window, console*/

jQuery(function($) {

    // No globals, dude!
    "use strict";

    var dataGridField2Functions = {};

    /**
     * Get edit mode of the DGF instance
     *
     * @return {String} "row" or "block"
     */
    dataGridField2Functions.getMode = function(node) {
         var dgf = $(dataGridField2Functions.getParentByClass(node, "datagridwidget-table-view"));
         return dgf.attr("data-mode");
    };

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
    };

    dataGridField2Functions.getWidgetRows = function(currnode) {
        /* Return primary nodes with class of datagridwidget-row,
           they can be any tag: tr, div, etc. */
        var tbody = this.getParentByClass(currnode, "datagridwidget-body");
        return this.getRows(tbody);
    };

    dataGridField2Functions.getRows = function(tbody) {
        /* Return primary nodes with class of datagridwidget-row,
           they can be any tag: tr, div, etc. */

        var rows = $(tbody).children('.datagridwidget-row');

        return rows;
    };

    /**
     * Handle auto insert events
     */
    dataGridField2Functions.onInsert = function(e) {
        var currnode = window.event ? window.event.srcElement : e.currentTarget;
        this.autoInsertRow(currnode);
    },

    /**
     * Add a new row when changing the last row
     *
     *
     */
    dataGridField2Functions.autoInsertRow = function(currnode) {

        // fetch required data structure
        var dgf = $(dataGridField2Functions.getParentByClass(currnode, "datagridwidget-table-view"));
        var tbody = dataGridField2Functions.getParentByClass(currnode, "datagridwidget-body");
        var thisRow = dataGridField2Functions.getParentRow(currnode); // The new row we are working on

        // Remove the auto-append functionality from the all rows in this widget
        var autoAppendHandlers = dgf.find('.auto-append > .datagridwidget-cell, .auto-append > .datagridwidget-block-edit-cell');
        autoAppendHandlers.unbind('change.dgf');
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

        dgf.trigger("beforeaddrowauto", [dgf, newtr]);

        $(newtr).insertAfter(thisRow);

        // Re-enable auto-append change handler feature on the new auto-appended row
        $('.auto-append > .datagridwidget-cell, .auto-append > .datagridwidget-block-edit-cell').bind("change.dgf", dataGridField2Functions.onInsert);

        dataGridField2Functions.reindexRow(tbody, newtr, 'AA');

        // Update order index to give rows correct values
        dataGridField2Functions.updateOrderIndex(tbody, true);

        dgf.trigger("afteraddrowauto", [dgf, newtr]);
    };

    dataGridField2Functions.addRowAfter = function(currnode) {
        /*
            Creates a new row after the clicked row
        */

        // fetch required data structure
        var tbody = this.getParentByClass(currnode, "datagridwidget-body");
        var dgf = $(dataGridField2Functions.getParentByClass(currnode, "datagridwidget-table-view"));

        var thisRow = this.getParentRow(currnode);

        var newtr = this.createNewRow(thisRow);

        dgf.trigger("beforeaddrow", [dgf, newtr]);

        if (thisRow.hasClass('auto-append') === true) {
            $(newtr).insertBefore(thisRow);
        } else {
            $(newtr).insertAfter(thisRow);
        }

        // update orderindex hidden fields
        this.updateOrderIndex(tbody,true);

        dgf.trigger("afteraddrow", [dgf, newtr]);

    };

    /**
     * Creates a new row.
     *
     * The row is not inserted to the table, but is returned.
     *
     * @param {Object} <tr> or <tbody> DOM node in a table where we'll be adding the new row
     */
    dataGridField2Functions.createNewRow = function(node) {

        var tbody = this.getParentByClass(node, "datagridwidget-body");

        // hidden template row
        var emptyRow = $(tbody).children('.datagridwidget-empty-row');

        if(emptyRow.size() === 0) {
            // Ghetto assert()
            throw new Error("Could not locate empty template row in DGF");
        }

        var markup = emptyRow.clone(true);

        var newTr = markup.attr("class","datagridwidget-row");

        return newTr[0];
    };


    dataGridField2Functions.removeFieldRow = function(node) {
        /* Remove the row in which the given node is found */
        var tbody = this.getParentByClass(node, "datagridwidget-body");
        var row = this.getParentRow(node);
        $(row).remove();
        this.updateOrderIndex(tbody,false);
    };

    dataGridField2Functions.moveRow = function(currnode, direction){
        /* Move the given row down one */
        var nextRow;

        var dgf = $(dataGridField2Functions.getParentByClass(currnode, "datagridwidget-table-view"));

        var tbody = this.getParentByClass(currnode, "datagridwidget-body");

        var rows = this.getWidgetRows(currnode);

        var row = this.getParentRow(currnode);
        if(!row) {
            window.alert("Couldn't find DataGridWidget row");
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
        if(!idx)
            return;


        // The up and down should cycle through the rows, excluding the auto-append and
        // empty-row rows.
        var validrows = 0;
        rows.each(function (i) {
            if (!$(this).hasClass('datagridwidget-empty-row') && !$(this).hasClass('auto-append')) {
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

        } else if (idx === 0) {
            if (direction == "up") {
                this.moveRowToBottom(row);
            } else {
                nextRow = rows[parseInt(idx+1, 10)];
                this.shiftRow(row, nextRow);
            }

        } else {
            if (direction == "up") {
                nextRow = rows[idx-1];
                this.shiftRow(nextRow, row);
            } else {
                nextRow = rows[parseInt(idx+1, 10)];
                this.shiftRow(row, nextRow);
            }
        }

        this.updateOrderIndex(tbody);

        dgf.trigger("aftermoverow", [dgf]);
    };

    dataGridField2Functions.moveRowDown = function(currnode){
        this.moveRow(currnode, "down");
    };

    dataGridField2Functions.moveRowUp = function(currnode){
        this.moveRow(currnode, "up");
    };

    dataGridField2Functions.shiftRow = function(bottom, top){
        /* Put node top before node bottom */
        $(top).insertBefore(bottom);
    };

    dataGridField2Functions.moveRowToTop = function (row) {
        var rows = this.getWidgetRows(row);
        $(row).insertBefore(rows[0]);
    };

    dataGridField2Functions.moveRowToBottom = function (row) {
        var rows = this.getWidgetRows(row);

        // make sure we insert the directly above any auto appended rows
        var insert_after = 0;
        rows.each(function (i) {
            if (!$(this).hasClass('datagridwidget-empty-row')  && !$(this).hasClass('auto-append')) {
                insert_after = i;
            }
        });
        $(row).insertAfter(rows[insert_after]);
    };

    /**
     * Rename <input> controls so that each control has unique name
     * based on the row its on. On the server side, the
     * DGF logic will rebuild rows based on this information.
     *
     * If indexing for some reasons fails you'll get double
     * input values and Zope converts inputs to list, failing
     * in funny ways.
     *
     * @param  {DOM} tbody
     * @param  {DOM} row
     * @param  {Number} newindex
     */
    dataGridField2Functions.reindexRow = function (tbody, row, newindex) {
        var name_prefix = $(tbody).attr('data-name_prefix') + '.';
        var id_prefix = $(tbody).attr('data-id_prefix') + '-';
        var cells;
        var hidden = null;

        // console.log("Reindexing row " + newindex);
        //

        // Expand jQuery z3c.form widget selection to cover checkbox <input>s
        function expandAllZ3CFormInputs(sel) {
            var checkboxes = sel.children(".option");
            sel = sel.add(checkboxes);

            var datetimedropdowns = sel.children(".datetimepicker_input").find("select").parent();
            sel = sel.add(datetimedropdowns);

            return sel;
        }

        // We need to select
        // - all direct children inputs in row mode
        // - all direct children inputs in block mode
        // - but not nested inputs, as it would break nested datagridfields
        var mode = this.getMode(tbody);

        if(mode == "row") {
            // Select normal inputs, checkboxes
            cells = $(row).children("td");
            cells = expandAllZ3CFormInputs(cells);
        }  else if(mode == "block") {
            // We need to update hidden data rows also which are not rendered as blocks
            cells = $(row).children("td").children(".datagridwidget-block");
            // Checkboxes
            cells = expandAllZ3CFormInputs(cells);
            hidden = $(row).children(".datagridwidget-hidden-data");
            cells = cells.add(hidden); // AA and TT row stuff
        } else {
            throw new Error("Unknown DGF mode:" + mode);
        }


        // Math all <input> by name on the row which fields' names we update
        var inputs = cells.children('[name^="' + name_prefix +'"]');

        inputs.each(function(){

            //console.log("Got: " + this.name);
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

        cells.children('[id*="' + id_prefix +'"]').each(function(){
            var regexp = new RegExp(id_prefix + ".*?-");
            this.id = this.id.replace(regexp, id_prefix + newindex + "-");
        });

        cells.children('[for*="' + id_prefix +'"]').each(function(){
            var regexp = new RegExp(id_prefix + ".*?-");
            this.setAttribute('for', this.getAttribute('for').replace(regexp, id_prefix + newindex + "-"));
        });

        cells.children('[class*="' + name_prefix +'"]').each(function(){
            var regexp = new RegExp(name_prefix + ".*?\\.");
            this.className = this.className.replace(regexp, name_prefix + newindex + ".");
        });
    };


    /**
     * Update all row indexes on a DGF table.
     *
     * @param  {Object} tbody     [description]
     * @param  {Boolean} backwards [description]
     */
    dataGridField2Functions.updateOrderIndex = function (tbody, backwards) {

        /* Split from the dataGridField2 approach here - and just re-do
         * the numbers produced by z3c.form
         */
        var name_prefix = $(tbody).attr('data-name_prefix') + '.';
        var i, idx, row, $row, $nextRow;

        // Was this auto-append table
        var autoAppend = false;

        var rows = this.getRows(tbody);
        for (i=0; i<rows.length; i++) {
            idx = backwards ? rows.length-i-1 : i;
            row = rows[idx], $row = $(row);

            if ($row.hasClass('datagridwidget-empty-row')) {
                continue;
            }

            if($row.hasClass('auto-append')) {
                autoAppend = true;
            }

            dataGridField2Functions.reindexRow(tbody, row, idx);
        }

        // Add a special first and class row classes
        // to hide manipulation handles
        // (AA and TT doesn't count here)
        if(autoAppend) {
            for (i=0; i<rows.length; i++) {
                row = rows[i], $row = $(row);

                if(i<rows.length) {
                    $nextRow = $(rows[i+1]);
                }

                if(i===0) {
                    $row.addClass("datagridfield-first-filled-row");
                } else {
                    $row.removeClass("datagridfield-first-filled-row");
                }

                // Last visible before AA
                if($nextRow && $nextRow.hasClass("auto-append")) {
                    $row.addClass("datagridfield-last-filled-row");
                } else {
                    $row.removeClass("datagridfield-last-filled-row");
                }
            }
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
    };

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
    };

    dataGridField2Functions.getParentRow = function (node) {
        return this.getParentByClass(node, 'datagridwidget-row');
    };

    dataGridField2Functions.getParentByClass = function(node, klass) {
        var parent = $(node).closest("." + klass);

        if (parent.length) {
            return parent;
        }

        return null;
    };

    /**
     * Find the first parent node with the given id
     *
     * Id is partially matched: the beginning of
     * an element id matches parameter id string.
     *
     * @param  {DOM} currnode Node where ascending in DOM tree beings
     * @param  {String} id       Id string to look for.
     * @return {DOM} Found node or null
     */
    dataGridField2Functions.getParentElementById = function(currnode, id) {
        /*
        */

        id = id.toLowerCase();
        var parent = currnode.parentNode;

        while(true) {

            var parentId = parent.getAttribute("id");
            if(parentId) {
                 if(parentId.toLowerCase().substring(0, id.length) == id) break;
            }

            parent = parent.parentNode;
            // Next line is a safety belt
            if(parent.tagName.toUpperCase() == "BODY")
                return null;
        }

        return parent;
    };


    /**
     * Make sure there is at least one visible row available in DGF
     * to edit in all the time.
     *
     * There are cases where one doesn't want to have the count of DGF
     * rows to go down to zero. Otherwise there no insert handle left
     * on the edit mode and the user cannot add any more rows.
     *
     * One should case is when
     *
     * - DGF is empty (new form)
     *
     * - Auto append is set to false (initial row is not visible)
     *
     * We fix this situation by checking the available rows
     * and generating one empty AA row if needed.
     *
     * ... or simply when the user removes all the rows
     *
     * @param {Object} tbody DOM object of <tbody>
     */
    dataGridField2Functions.ensureMinimumRows = function(tbody) {
        var rows = this.getRows(tbody);
        var self = this;

        // We rape jQuery.filter here, because of
        // IE8 Array.filter http://kangax.github.com/es5-compat-table/

        // Consider "real" rows only
        var filteredRows = $(rows).filter(function() {
            var $tr = $(this);
            return !$tr.hasClass("datagridwidget-empty-row");
        });

        // Rows = 0 -> make one AA row available
        if(filteredRows.length === 0) {
            // XXX: make the function call signatures more sane
            var child = rows[0];
            this.autoInsertRow(child);
        }
    },


    /**
     * When DOM model is ready execute this actions to wire up page logic.
     */
    dataGridField2Functions.init = function() {

        // Bind the handlers to the auto append rows
        // Use namespaced jQuery events to avoid unbind() conflicts later on
        $('.auto-append > .datagridwidget-cell, .auto-append > .datagridwidget-block-edit-cell').bind("change.dgf", dataGridField2Functions.onInsert);

        // Reindex all rows to get proper row classes on them
        $(".datagridwidget-body").each(function() {
            dataGridField2Functions.updateOrderIndex(this, false);
            dataGridField2Functions.ensureMinimumRows(this);
        });

        $(document).trigger("afterdatagridfieldinit");
    };


    $(document).ready(dataGridField2Functions.init);

    // Export module for customizers to mess around
    window.dataGridField2Functions = dataGridField2Functions;


});
