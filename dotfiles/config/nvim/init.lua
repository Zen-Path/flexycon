vim.g.mapleader = ","

local fn = vim.fn
local install_path = fn.stdpath("config") .. "/autoload/plug.vim"

if fn.empty(fn.glob(install_path)) > 0 then
    print("Downloading junegunn/vim-plug to manage plugins...")
    fn.system({ "mkdir", "-p", vim.fn.stdpath("config") .. "/autoload" })
    fn.system({
        "curl",
        "-fLo",
        install_path,
        "--create-dirs",
        "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
    })
    vim.cmd([[autocmd VimEnter * PlugInstall]])
end

vim.cmd([[
  call plug#begin(stdpath('config') . '/plugged')
    Plug 'luisiacc/gruvbox-baby'
    Plug 'tpope/vim-surround'
    Plug 'preservim/nerdtree'
    Plug 'junegunn/goyo.vim'
    Plug 'jreybert/vimagit'
    Plug 'vimwiki/vimwiki'
    Plug 'vim-airline/vim-airline'
    Plug 'tpope/vim-commentary'
    Plug 'ap/vim-css-color'
    Plug 'lambdalisue/vim-suda'
  call plug#end()
]])

-- FILES
local data_home = os.getenv("XDG_DATA_HOME")
    or (os.getenv("HOME") .. "/.local/share")

local nvim_data = data_home .. "/nvim"
local undo_dir = nvim_data .. "/undo//"
local backup_dir = nvim_data .. "/backup//"

-- Ensure the dirs (and any parents) exist
for _, dir in ipairs({ undo_dir, backup_dir }) do
    if vim.fn.isdirectory(dir) == 0 then
        vim.fn.mkdir(dir, "p")
    end
end

-- THEME
vim.g.gruvbox_baby_transparent_mode = 1
vim.cmd.colorscheme("gruvbox-baby")

-- EDITOR
vim.opt.title = true
vim.opt.background = "dark"
vim.opt.mouse = "a"
vim.opt.hlsearch = false
vim.opt.clipboard:append("unnamedplus")
vim.opt.showmode = false
vim.opt.ruler = false
vim.opt.laststatus = 0
vim.opt.showcmd = false
vim.opt.ignorecase = true
vim.opt.smartcase = true

-- TAB vs SPACES
vim.opt.expandtab = true -- Use spaces instead of tabs
vim.opt.tabstop = 4 -- Visual width of '\t' characters
vim.opt.shiftwidth = 4 -- Indentation width for << and >>
vim.opt.smartindent = true -- Smart auto-indenting

vim.opt.softtabstop = 4 -- Number of spaces inserted when pressing <Tab>
vim.opt.autoindent = true -- Copy indent from current line when starting a new one

-- BACKUPS and HISTORY

-- Persistent undo
-- Keep undo history accessible across restarts.
vim.opt.undofile = true
vim.opt.undodir = undo_dir

-- Backups
-- Restore the last saved-on-disk version
vim.opt.backup = true -- Keep a copy before overwriting
vim.opt.writebackup = true -- Keep a temp copy during the write
vim.opt.backupdir = backup_dir

-- KEY MAPPINGS
local map = vim.keymap.set
local opts = { noremap = true, silent = true }

-- Don't yank when changing with 'c'
map("n", "c", [["_c]], opts)

-- Dot-repeat for visual selections
map("v", ".", ":normal .<CR>", opts)

-- Goyo prose mode toggle
map("n", "<leader>f", ":Goyo | set bg=light | set linebreak<CR>", opts)

-- Toggle spell check
map("n", "<leader>o", ":setlocal spell! spelllang=en_us<CR>", opts)

-- Redo with U
map("n", "U", ":redo<CR>", opts)

-- Replace all
map("n", "S", ":%s//g<Left><Left>", opts)

-- Replace Ex mode with gq
map("n", "Q", "gq", opts)

-- Run shellcheck
map("n", "<leader>s", ":!clear && shellcheck -x %<CR>", opts)

-- Write to files that require sudo
vim.api.nvim_set_keymap(
    "c", -- in command-line mode
    "w!!", -- what you type
    "SudaWrite", -- what it expands to
    { noremap = true, silent = false } -- set silent to false to see the expansion
)

vim.keymap.set("n", ",,", [[:keepp /<++><CR>ca<]], opts)
vim.keymap.set("i", ",,", [[<Esc>:keepp /<++><CR>ca<]], opts)

-- CUSTOM COMMANDS
vim.api.nvim_create_user_command("DelEmpty", "%g/^$/d", {})
vim.api.nvim_create_user_command("ReduceEmpty", function()
    vim.cmd([[%s/\v(\n\s*){2,}/\r\r/g]])
end, {})

vim.api.nvim_create_autocmd("BufWritePre", {
    pattern = "*",
    callback = function()
        -- Save current cursor position
        local pos = vim.fn.getpos(".")

        -- Remove trailing spaces
        vim.cmd([[%s/\s\+$//e]])

        -- Remove extra blank lines at EOF
        vim.cmd([[%s/\n\+\%$//e]])

        -- Add exactly one newline at EOF
        local last_line = vim.fn.line("$")
        local last_line_content = vim.fn.getline(last_line)
        if last_line_content ~= "" then
            vim.fn.append(last_line, "")
        end

        -- Restore cursor position
        vim.fn.setpos(".", pos)
    end,
})

-- GENERAL
vim.opt.compatible = false -- Not strictly needed, Neovim is always 'nocompatible'
vim.cmd([[filetype plugin on]]) -- No Lua API for this, keep as vim.cmd
vim.cmd([[syntax on]]) -- Likewise, still VimL

vim.opt.encoding = "utf-8"
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.wildmode = { "longest", "list", "full" }
vim.opt.splitbelow = true
vim.opt.splitright = true

vim.api.nvim_create_autocmd("FileType", {
    pattern = "*",
    callback = function()
        vim.opt_local.formatoptions:remove({ "c", "r", "o" })
    end,
})

-- Load command shortcuts generated from bm-dirs and bm-files via user shortcuts script.
local shortcuts_file = vim.fn.expand("~/.config/nvim/shortcuts.vim")
if vim.fn.filereadable(shortcuts_file) == 1 then
    vim.cmd("silent! source " .. shortcuts_file)
end
