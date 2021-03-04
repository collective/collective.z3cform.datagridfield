// IE NodeList.forEach polyfill.
// See: https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach#polyfill
if (window.NodeList && !NodeList.prototype.forEach) {
    NodeList.prototype.forEach = Array.prototype.forEach;
}

define(["jquery", "pat-base", "pat-registry"], function ($, Base, Registry) {
    var pattern = Base.extend({
        name: "datagridfield",
        trigger: ".pat-datagridfield",

        init: function () {
            // - Make sure, at least one empty row is always shown.
            // - Auto append a new row when editing the last row.

            this.el = this.$el[0];
            this.el_body = this.el.querySelector(".datagridwidget-body");

            this.auto_append = (this.el.dataset.autoAppend || "true").toLowerCase() !== "false"; // prettier-ignore

            // Hint CSS
            if (this.auto_append) {
                this.el_body.classList.add("datagridwidget-body-auto-append");
            } else {
                this.el_body.classList.add("datagridwidget-body-non-auto-append"); // prettier-ignore
            }

            this._defineHandler();

            this.updateOrderIndex(false);

            // Before ensureMinimumRows, as creating a row initializes row ui again.
            this.getVisibleRows().forEach(function (row) {
                this.initRowUI(row);
            }, this);

            this.ensureMinimumRows();
            this.initAutoAppendHandler();

            this.el.dispatchEvent(
                new Event("afterdatagridfieldinit", {
                    bubbles: true,
                    cancelable: true,
                })
            );
        },

        _defineHandler: function () {
            // Store event handler which also has to be removed, so we can detach it.
            // See: https://stackoverflow.com/a/10444156/1337474 , also comment about "bind"
            // using ``bind`` will change the function signature too.

            this.handler_auto_append = function (e) {
                if (e) {
                    e.stopPropagation();
                }
                // Also allow direct call without event.
                if (e && !e.target.closest(".datagridwidget-cell")) {
                    return;
                }
                this.auto_append_row();
            }.bind(this);

            this.handler_auto_append_input = function (e) {
                var row = e.currentTarget;
                row.classList.remove("auto-append");
                this.updateOrderIndex();
                row.removeEventListener(
                    "input",
                    this.handler_auto_append_input
                );
            }.bind(this);
        },

        initRowUI: function (row) {
            row.querySelectorAll(".dgf--row-add").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.insertRow(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-delete").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.removeFieldRow(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-moveup").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.moveRowUp(row);
                    }.bind(this)
                );
            }, this);

            row.querySelectorAll(".dgf--row-movedown").forEach(function (el) {
                el.addEventListener(
                    "click",
                    function (e) {
                        e.preventDefault();
                        this.moveRowDown(row);
                    }.bind(this)
                );
            }, this);
        },

        getRows: function () {
            // Return primary nodes with class of datagridwidget-row, they can be any tag: tr, div, etc.
            return this.el_body.querySelectorAll(".datagridwidget-row");
        },

        getVisibleRows: function () {
            return this.el_body.querySelectorAll(
                ".datagridwidget-row:not(.datagridwidget-empty-row)"
            );
        },

        getLastRow: function () {
            return this.el_body.querySelector(".datagridwidget-row:last-child");
        },

        getLastVisibleRow: function () {
            var result = this.el_body.querySelectorAll(
                ".datagridwidget-row:not(.datagridwidget-empty-row)"
            );
            return result[result.length - 1];
        },

        initAutoAppendHandler: function () {
            if (!this.auto_append) {
                return;
            }

            this.getVisibleRows().forEach(function (row) {
                row.removeEventListener("focusout", this.handler_auto_append);
            }, this);

            var last_row = this.getLastVisibleRow();
            if (last_row) {
                last_row.addEventListener("focusout", this.handler_auto_append);
            }
        },

        auto_append_row: function () {
            this.el.dispatchEvent(new Event("beforeaddrowauto"));
            this.getVisibleRows().forEach(function (row) {
                row.classList.remove("auto-append");
            });
            var last_row = this.getLastVisibleRow() || this.getLastRow();
            var new_row = this.insertRow(last_row);
            new_row.classList.add("auto-append");
            this.reindexRow(new_row, "AA");
            new_row.addEventListener("input", this.handler_auto_append_input);
            this.el.dispatchEvent(new Event("afteraddrowauto"));
        },

        insertRow: function (ref_row, ensureMinimumRows, before) {
            /**
             * Add a new row when changing the last row
             *
             * @param {DOM node} ref_row insert row after this one.
             * @param {Boolean} ensureMinimumRows: we insert a special minimum row so the widget is not empty
             */

            // Create a new row
            var newtr = this.createNewRow();
            var $newtr = $(newtr);

            /* Put new row to DOM tree after our current row.  Do this before
             * reindexing to ensure that any Javascript we insert that depends on
             * DOM element IDs (such as plone.formwidget.autocomplete) will
             * pick up this row before any IDs get changed.  At this point,
             * we techinically have duplicate TT IDs in our document
             * (one for this new row, one for the hidden row), but jQuery
             * selectors will pick up elements in this new row first.
             */

            this.$el.trigger("beforeaddrow", [this.$el, $newtr]);

            if (before) {
                $newtr.insertBefore(ref_row);
            } else {
                $newtr.insertAfter(ref_row);
            }

            // Update order index to give rows correct values
            this.updateOrderIndex(true, ensureMinimumRows);

            this.initAutoAppendHandler();

            this.$el.trigger("afteraddrow", [this.$el, $newtr]);

            return newtr;
        },

        createNewRow: function () {
            /**
             * Creates a new row.
             *
             * The row is not inserted to the table, but is returned.
             */

            // hidden template row
            var template_row = this.el_body.querySelector(
                ".datagridwidget-empty-row"
            );
            if (!template_row) {
                throw new Error("Could not locate empty template row in DGF");
            }

            var new_row = template_row.cloneNode(true);
            new_row.classList.remove("datagridwidget-empty-row");

            this.initRowUI(new_row);

            var $new_row = $(new_row);
            // enable patternslib
            $new_row
                .find('*[class^="dgw-disabled-pat-"]')
                .attr("class", function (i, cls) {
                    return cls.replace(/dgw\-disabled-pat-/, "pat-");
                });
            Registry.scan($new_row);
            return new_row;
        },

        removeFieldRow: function (row) {
            /* Remove the row in which the given node is found */
            $(row).remove();

            // ensure minimum rows.
            // if no minimal row was added, reindex.
            // otherwise reindexing is done by insertRow
            if (!this.ensureMinimumRows()) {
                this.updateOrderIndex(false);
            }

            this.initAutoAppendHandler();
        },

        moveRowDown: function (row) {
            this.moveRow(row, "down");
            this.initAutoAppendHandler();
        },

        moveRowUp: function (row) {
            this.moveRow(row, "up");
            this.initAutoAppendHandler();
        },

        moveRowToTop: function (row) {
            var rows = this.getRows();
            $(row).insertBefore(rows[0]);
            this.initAutoAppendHandler();
        },

        moveRowToBottom: function (row) {
            var rows = this.getRows();

            // make sure we insert the directly above any auto appended rows
            var insert_after = 0;
            $(rows).each(function (i) {
                if (
                    !$(this).hasClass("datagridwidget-empty-row") &&
                    !$(this).hasClass("auto-append")
                ) {
                    insert_after = i;
                }
            });
            $(row).insertAfter(rows[insert_after]);
            this.initAutoAppendHandler();
        },

        moveRow: function (row, direction) {
            /* Move the given row down one */
            var nextRow;
            var rows = this.getRows();
            var idx = null;

            // We can't use nextSibling because of blank text nodes in some browsers
            // Need to find the index of the row
            $(rows).each(function (i) {
                if (this == row) {
                    idx = i;
                }
            });

            // Abort if the current row wasn't found
            if (idx == null) return;

            // The up and down should cycle through the rows, excluding the auto-append and
            // empty-row rows.
            var validrows = 0;
            $(rows).each(function (i) {
                if (
                    !$(this).hasClass("datagridwidget-empty-row") &&
                    !$(this).hasClass("auto-append")
                ) {
                    validrows += 1;
                }
            });

            if (idx + 1 == validrows) {
                if (direction == "down") {
                    this.moveRowToTop(row);
                } else {
                    nextRow = rows[idx - 1];
                    this.shiftRow(nextRow, row);
                }
            } else if (idx === 0) {
                if (direction == "up") {
                    this.moveRowToBottom(row);
                } else {
                    nextRow = rows[parseInt(idx + 1, 10)];
                    this.shiftRow(row, nextRow);
                }
            } else {
                if (direction == "up") {
                    nextRow = rows[idx - 1];
                    this.shiftRow(nextRow, row);
                } else {
                    nextRow = rows[parseInt(idx + 1, 10)];
                    this.shiftRow(row, nextRow);
                }
            }
            this.updateOrderIndex();
            this.$el.trigger("aftermoverow", [this.$el, row]);
        },

        shiftRow: function (bottom, top) {
            /* Put node top before node bottom */
            $(top).insertBefore(bottom);
        },

        reindexRow: function (row, newindex) {
            /**
             * Fixup all attributes on all child elements that contain
             * the row index. The following attributes are scanned:
             * - name
             * - id
             * - for
             * - href
             * - data-fieldname
             *
             * On the server side, the DGF logic will rebuild rows based
             * on this information.
             *
             * If indexing for some reasons fails you'll get double
             * input values and Zope converts inputs to list, failing
             * in funny ways.
             *
             * @param  {DOM} row
             * @param  {Number} newindex
             */

            var $tbody = $(this.el_body);
            var name_prefix = $tbody.data("name_prefix") + ".";
            var id_prefix = $tbody.data("id_prefix") + "-";
            var $row = $(row);
            var oldindex = $row.data("index");

            function replaceIndex(el, attr, prefix) {
                if (el.attr(attr)) {
                    var val = el.attr(attr);
                    var pattern = new RegExp("^" + prefix + oldindex);
                    el.attr(attr, val.replace(pattern, prefix + newindex));
                    if (attr.indexOf("data-") === 0) {
                        var key = attr.substr(5);
                        var data = el.data(key);
                        el.data(key, data.replace(pattern, prefix + newindex));
                    }
                }
            }

            // update index data
            $row.data("index", newindex);
            $row.attr("data-index", newindex);

            $row.find('[id^="formfield-' + id_prefix + '"]').each(function (
                i,
                el
            ) {
                replaceIndex($(el), "id", "formfield-" + id_prefix);
            });
            $row.find('[name^="' + name_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "name", name_prefix);
            });
            $row.find('[id^="' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "id", id_prefix);
            });
            $row.find('[for^="' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "for", id_prefix);
            });
            $row.find('[href*="#' + id_prefix + '"]').each(function (i, el) {
                replaceIndex($(el), "href", "#" + id_prefix);
            });
            $row.find('[data-fieldname^="' + name_prefix + '"]').each(function (
                i,
                el
            ) {
                replaceIndex($(el), "data-fieldname", name_prefix);
            });
        },

        updateOrderIndex: function (backwards, ensureMinimumRows) {
            /**
             * Update all row indexes on a DGF table.
             *
             * Each <tr> and input widget has recalculated row index number in its name,
             * so that the server can then parsit the submitted data in the correct order.
             *
             * @param  {Boolean} backwards iterate rows backwards
             * @param  {Boolean} ensureMinimumRows We have inserted a special auto-append row
             */

            var $tbody = $(this.el_body);
            var name_prefix = $tbody.attr("data-name_prefix") + ".";
            var i, idx, row, $row, $nextRow;

            // Was this auto-append table
            var autoAppend = false;
            var rows = this.getRows();
            for (i = 0; i < rows.length; i++) {
                idx = backwards ? rows.length - i - 1 : i;
                (row = rows[idx]), ($row = $(row));

                if ($row.hasClass("datagridwidget-empty-row")) {
                    continue;
                }
                if ($row.hasClass("auto-append")) {
                    autoAppend = true;
                }
                this.reindexRow(row, idx);
            }

            // Handle a special case where
            // 1. Widget is empty
            // 2. We don't have AA mode turned on
            // 3. We need to have minimum editable row count of 1
            if (ensureMinimumRows) {
                this.reindexRow(rows[0], "AA");
                autoAppend = true;
            }

            // Add a special first and class row classes
            // to hide manipulation handles
            // AA handling is different once again
            var visibleRows = this.getVisibleRows();
            for (i = 0; i < visibleRows.length; i++) {
                (row = visibleRows[i]), ($row = $(row));
                if (i < visibleRows.length - 2) {
                    $nextRow = $(visibleRows[i + 1]);
                }
                if (i === 0) {
                    $row.addClass("datagridfield-first-filled-row");
                } else {
                    $row.removeClass("datagridfield-first-filled-row");
                }
                // Last visible before AA
                if (autoAppend) {
                    if ($nextRow && $nextRow.hasClass("auto-append")) {
                        $row.addClass("datagridfield-last-filled-row");
                    } else {
                        $row.removeClass("datagridfield-last-filled-row");
                    }
                } else {
                    if (i == visibleRows.length - 1) {
                        $row.addClass("datagridfield-last-filled-row");
                    } else {
                        $row.removeClass("datagridfield-last-filled-row");
                    }
                }
            }

            // Set total visible row counts and such and hint CSS
            var vis = this.getVisibleRows().length;
            $tbody.attr("data-count", this.getRows().length);
            $tbody.attr("data-visible-count", this.getVisibleRows().length);
            $tbody.attr("data-many-rows", vis >= 2 ? "true" : "false");

            $(document)
                .find('input[name="' + name_prefix + 'count"]')
                .each(function () {
                    // do not include the TT and the AA rows in the count
                    var count = rows.length;
                    if (
                        $(rows[count - 1]).hasClass("datagridwidget-empty-row")
                    ) {
                        count--;
                    }
                    if ($(rows[count - 1]).hasClass("auto-append")) {
                        count--;
                    }
                    this.value = count;
                });
        },

        getParentRow: function (node) {
            var parent = node.closest(".datagridwidget-row");
            if (parent) {
                return parent;
            }
            return null;
        },

        ensureMinimumRows: function () {
            /**
             * Make sure there is at least one visible row available in DGF
             * to edit in all the time.
             *
             * We need a lot of special logic for the case where
             * we have empty datagridfield and need to have one OPTIONAL
             * row present there for the editing when the user opens
             * the form for the first time.
             *
             * There are cases where one doesn't want to have the count of DGF
             * rows to go down to zero. Otherwise there no insert handle left
             * on the edit mode and the user cannot add any more rows.
             *
             * One should case is when
             *
             * - DGF is empty on new form
             *
             * - Auto append is set to false (initial row is not visible)
             *
             * We fix this situation by checking the available rows
             * and generating one empty AA row if needed.
             *
             * ... or simply when the user removes all the rows
             */

            var rows = this.getRows();
            var filteredRows = this.getVisibleRows();

            // Rows = 0 -> make one AA row available
            if (rows.length && filteredRows.length === 0) {
                this.auto_append_row();
                return true;
            }
            return false;
        },
    });

    return pattern;
});
