--[[
Concordia University front pages, for Word output.

Builds what the School of Graduate Studies' thesis templates (doctoral and
master's) put before the first chapter, from the `concordia:` settings in
_quarto-concordia.yml:

  title page and signature page   counted i and ii, no number shown
  abstract, optional pages,       lower-case roman from iii
  table of contents, lists
  chapters                        arabic from 1 (reference.docx's own section)

The wording follows the official templates.
]]

local common = dofile(quarto.utils.resolve_path("../common.lua"))
local stringify, esc, raw, line = common.stringify, common.esc, common.raw, common.line

-- Concordia: letter paper, one-inch margins.
local PAGE = '<w:pgSz w:w="12240" w:h="15840"/>'
  .. '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'

-- One paragraph of text and tabs, as raw Word XML: "By:<tab>name". `stops`
-- are tab positions in twentieths of a point (1440 = one inch); `before` is
-- space above the paragraph, in the same unit.
local function tabbed(parts, stops, before)
  local tabs = {}
  for _, pos in ipairs(stops or {}) do
    tabs[#tabs + 1] = '<w:tab w:val="left" w:pos="' .. pos .. '"/>'
  end
  local runs = {}
  for i, p in ipairs(parts) do
    if i > 1 then runs[#runs + 1] = '<w:r><w:tab/></w:r>' end
    runs[#runs + 1] = '<w:r><w:t xml:space="preserve">' .. esc(p) .. '</w:t></w:r>'
  end
  return raw('<w:p><w:pPr><w:pStyle w:val="FrontText"/>'
    .. (#tabs > 0 and ('<w:tabs>' .. table.concat(tabs) .. '</w:tabs>') or '')
    .. '<w:spacing w:before="' .. (before or 0) .. '" w:after="120"/></w:pPr>'
    .. table.concat(runs) .. '</w:p>')
end

-- The examining committee: a borderless two-column table, signature line
-- and name on the left, role on the right, as in the official template.
local function committee_table(members)
  local rows = {}
  for _, m in ipairs(members) do
    local cell = function(text, width)
      return '<w:tc><w:tcPr><w:tcW w:w="' .. width .. '" w:type="dxa"/></w:tcPr>'
        .. '<w:p><w:pPr><w:spacing w:before="360" w:after="0"/></w:pPr><w:r><w:t xml:space="preserve">'
        .. esc(text) .. '</w:t></w:r></w:p></w:tc>'
    end
    rows[#rows + 1] = '<w:tr>'
      .. cell('_________________________________ ' .. stringify(m.name or ''), 6480)
      .. cell(stringify(m.role or ''), 2880) .. '</w:tr>'
  end
  return raw('<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>'
    .. '<w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
    .. '<w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders></w:tblPr>'
    .. '<w:tblGrid><w:gridCol w:w="6480"/><w:gridCol w:w="2880"/></w:tblGrid>'
    .. table.concat(rows) .. '</w:tbl>')
end

function Pandoc(doc)
  if not FORMAT:match("docx") then return nil end
  local c = doc.meta.concordia
  if not c then return nil end
  local footer = common.footer_rid(quarto.utils.resolve_path("footer.txt"), "concordia")

  local doctoral = stringify(c["degree-level"] or "doctoral") ~= "masters"
  local title, author = stringify(c.title or ""), stringify(c.author or "")
  local department, degree = stringify(c.department or ""), stringify(c.degree or "")
  local date, year = stringify(c.date or ""), stringify(c.year or "")

  local out = pandoc.Blocks({})

  -- Title page (i, unnumbered).
  out:insert(line("Front Title", title))
  for _, t in ipairs({ author, "A Thesis", "In the Department", "of", department,
    "Presented in Partial Fulfillment of the Requirements" }) do
    out:insert(line("Front Centered", t))
  end
  if doctoral then
    out:insert(line("Front Centered", "For the Degree of"))
    out:insert(line("Front Centered", degree))
    out:insert(line("Front Centered", "at Concordia University"))
  else
    out:insert(line("Front Centered", "for the Degree of " .. degree .. " at"))
    out:insert(line("Front Centered", "Concordia University"))
  end
  out:insert(line("Front Centered", "Montréal, Québec, Canada"))
  out:insert(line("Front Centered", date))
  out:insert(line("Front Centered", "© " .. author .. ", " .. year))

  -- Signature page (ii, unnumbered).
  out:insert(common.PAGE_BREAK)
  out:insert(line("Front Heading", "CONCORDIA UNIVERSITY"))
  out:insert(line("Front Heading", "SCHOOL OF GRADUATE STUDIES"))
  out:insert(line("Front Text", "This is to certify that the thesis prepared"))
  out:insert(tabbed({ "By:", author }, { 2160 }))
  out:insert(tabbed({ "Entitled:", title }, { 2160 }))
  out:insert(line("Front Text", "and submitted in partial fulfillment of the requirements for the degree of"))
  out:insert(line("Front Centered", doctoral and degree:upper() or degree))
  out:insert(line("Front Text", "complies with the regulations of the University and meets the accepted standards with respect to originality and quality."))
  out:insert(line("Front Text", "Signed by the final examining committee:"))
  out:insert(committee_table(c.committee or {}))
  local director = stringify(c["program-director"] or (doctoral and "Graduate Program Director"
    or "Chair of Department or Graduate Program Director"))
  local dean = stringify(c.dean or (doctoral and "Dean" or "Dean of Faculty"))
    .. (c.faculty and (", " .. stringify(c.faculty)) or "")
  out:insert(tabbed({ "Approved by", "_______________________________________________" }, { 2160 }, 480))
  out:insert(tabbed({ "", director }, { 2160 }))
  out:insert(tabbed({ "__________________", "_______________________________________________" }, { 2880 }, 480))
  out:insert(tabbed({ "Date", dean }, { 2880 }))
  out:insert(common.section_break(PAGE, '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>', nil))

  -- Abstract (iii) and the optional pages.
  out:insert(line("Front Heading", "Abstract"))
  out:insert(line("Front Centered", title))
  out:insert(line("Front Centered", doctoral and (author .. ", " .. stringify(c["degree-short"] or "Ph.D.")) or author))
  if doctoral then out:insert(line("Front Centered", "Concordia University, " .. year)) end
  out:extend(common.blocks_of(c.abstract) or pandoc.Blocks({}))
  common.optional_page(out, "Front Heading", "Summary", c.summary)
  common.optional_page(out, "Front Heading", "Acknowledgments", c.acknowledgments)
  common.optional_page(out, "Front Heading", "Dedication", c.dedication)
  common.optional_page(out, "Front Heading", "Contribution of Authors", c["contribution-of-authors"])
  local lists = {}
  if c["list-of-figures"] ~= false then lists[#lists + 1] = { title = "List of Figures", style = "Image Caption" } end
  if c["list-of-tables"] ~= false then lists[#lists + 1] = { title = "List of Tables", style = "Table Caption" } end
  common.contents_and_lists(out, "Front Heading", "Table of Contents", lists)
  out:insert(common.section_break(PAGE, '<w:pgNumType w:fmt="lowerRoman" w:start="3"/>', footer))

  common.drop_title_block(doc.meta)
  doc.blocks = out .. doc.blocks
  return doc
end
