--[[
Shared by the universities' front-page filters (concordia/, stanford/).

The front pages are built as pandoc blocks and, where pandoc has no
equivalent, raw Word XML: page breaks, section breaks (each carrying its own
page numbering) and fields (table of contents, lists of figures and tables).
Load with:  local common = dofile(quarto.utils.resolve_path("../common.lua"))
]]

local M = {}

M.stringify = pandoc.utils.stringify

function M.esc(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

function M.raw(xml) return pandoc.RawBlock("openxml", xml) end

M.PAGE_BREAK = M.raw('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

-- reference.docx's page-number footer. pandoc keeps the reference's
-- relationship ids; `pixi run <university>` writes this one to footer.txt
-- beside the filter when it builds reference.docx.
function M.footer_rid(path, task)
  local f = io.open(path, "r")
  if not f then
    error(path .. " is missing: run `pixi run " .. task .. "` first.")
  end
  local rid = f:read("*l")
  f:close()
  return rid
end

-- Ends a section. `page` is its <w:pgSz>/<w:pgMar>, `numbering` its
-- <w:pgNumType>, and `footer` the footer's relationship id, or nil for a
-- section whose pages show no number.
function M.section_break(page, numbering, footer)
  return M.raw('<w:p><w:pPr><w:sectPr>'
    .. (footer and ('<w:footerReference w:type="default" r:id="' .. footer .. '"/>') or '')
    .. page .. numbering .. '</w:sectPr></w:pPr></w:p>')
end

-- A paragraph in one of reference.docx's front-page styles.
function M.styled(style, inlines)
  return pandoc.Div({ pandoc.Para(inlines) }, pandoc.Attr("", {}, { { "custom-style", style } }))
end

function M.line(style, text) return M.styled(style, { pandoc.Str(text) }) end

-- A Word field (table of contents, list of figures): Word fills it when the
-- document is opened; tools/pdf.py updates it before making the PDF.
function M.field(instruction, placeholder)
  return M.raw('<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    .. '<w:r><w:instrText xml:space="preserve"> ' .. instruction .. ' </w:instrText></w:r>'
    .. '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    .. '<w:r><w:t>' .. M.esc(placeholder) .. '</w:t></w:r>'
    .. '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
end

-- Settings text (a string, inlines or Markdown blocks) as blocks.
function M.blocks_of(value)
  if value == nil then return nil end
  if pandoc.utils.type(value) == "Blocks" then return value end
  if pandoc.utils.type(value) == "Inlines" then return pandoc.Blocks({ pandoc.Para(value) }) end
  return pandoc.Blocks({ pandoc.Para({ pandoc.Str(M.stringify(value)) }) })
end

-- A page that appears only when its setting is filled in.
function M.optional_page(out, heading_style, heading, value)
  local content = M.blocks_of(value)
  if not content then return end
  out:insert(M.PAGE_BREAK)
  out:insert(M.line(heading_style, heading))
  out:extend(content)
end

-- The table of contents, then each list, every one on its own page. `lists`
-- is in the order the university wants, each { title, style } with style the
-- caption style it collects: pandoc writes "Image Caption" and "Table Caption".
function M.contents_and_lists(out, heading_style, contents_title, lists)
  out:insert(M.PAGE_BREAK)
  out:insert(M.line(heading_style, contents_title))
  out:insert(M.field('TOC \\o "1-3" \\h \\z \\u', "Table of contents: update fields to fill"))
  for _, list in ipairs(lists) do
    out:insert(M.PAGE_BREAK)
    out:insert(M.line(heading_style, list.title))
    out:insert(M.field('TOC \\h \\z \\t "' .. list.style .. ',1"', list.title .. ": update fields to fill"))
  end
end

-- The front pages replace Quarto's title block.
function M.drop_title_block(meta)
  for _, k in ipairs({ "title", "subtitle", "author", "date", "abstract" }) do meta[k] = nil end
end

return M
