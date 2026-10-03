--[[
Stanford University front pages, for Word output.

Builds the preliminary pages Stanford's format rules ask for, from the
`stanford:` settings in _quarto-stanford.yml:

  title page                      counts as i, not numbered
  (copyright ii, signature iii)   not in your file: Axess adds them
  abstract, optional pages,       lower-case roman from iv
  table of contents, lists
  chapters                        arabic from 1 (reference.docx's own section)

The title page follows Stanford's specimen pages: uppercase, centred, not
bold, no page number.
]]

local common = dofile(quarto.utils.resolve_path("../common.lua"))
local stringify, esc, raw, line = common.stringify, common.esc, common.raw, common.line

-- Stanford: letter paper, inner (left) margin 1.5 in, all others 1 in, page
-- numbers half an inch from the edge.
local PAGE = '<w:pgSz w:w="12240" w:h="15840"/>'
  .. '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="2160" w:header="720" w:footer="720" w:gutter="0"/>'

-- One line of the title page, `before` twentieths of a point below the last.
local function title_line(text, before)
  return raw('<w:p><w:pPr><w:pStyle w:val="TitlePageLine"/><w:spacing w:before="' .. (before or 0) .. '"/></w:pPr>'
    .. '<w:r><w:t xml:space="preserve">' .. esc(text:upper()) .. '</w:t></w:r></w:p>')
end

function Pandoc(doc)
  if not FORMAT:match("docx") then return nil end
  local s = doc.meta.stanford
  if not s then return nil end
  local footer = common.footer_rid(quarto.utils.resolve_path("footer.txt"), "stanford")

  local out = pandoc.Blocks({})

  -- Title page (i, unnumbered), laid out as Stanford's specimens.
  out:insert(title_line(stringify(s.title or "")))
  out:insert(title_line("A " .. stringify(s.document or "dissertation"), 2075))
  out:insert(title_line("Submitted to the " .. stringify(s["submitted-to"] or "")))
  out:insert(title_line("and the Committee on Graduate Studies"))
  out:insert(title_line("of Stanford University"))
  out:insert(title_line("in Partial Fulfillment of the Requirements"))
  out:insert(title_line("for the Degree of"))
  out:insert(title_line(stringify(s.degree or "Doctor of Philosophy")))
  out:insert(title_line(stringify(s.author or ""), 3185))
  out:insert(title_line(stringify(s.date or "")))
  out:insert(common.section_break(PAGE, '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>', nil))

  -- Abstract (iv: Axess adds the copyright page ii and signature page iii).
  out:insert(line("Front Heading", "Abstract"))
  out:extend(common.blocks_of(s.abstract) or pandoc.Blocks({}))
  common.optional_page(out, "Front Heading", "Preface", s.preface)
  common.optional_page(out, "Front Heading", "Acknowledgments", s.acknowledgments)
  common.optional_page(out, "Front Heading", "Dedication", s.dedication)
  local lists = {}
  if s["list-of-tables"] ~= false then lists[#lists + 1] = { title = "List of Tables", style = "Table Caption" } end
  if s["list-of-illustrations"] ~= false then lists[#lists + 1] = { title = "List of Illustrations", style = "Image Caption" } end
  common.contents_and_lists(out, "Front Heading", "Table of Contents", lists)
  out:insert(common.section_break(PAGE, '<w:pgNumType w:fmt="lowerRoman" w:start="4"/>', footer))

  common.drop_title_block(doc.meta)
  doc.blocks = out .. doc.blocks
  return doc
end
