local wezterm = require("wezterm")
local act = wezterm.action

local config = wezterm.config_builder()

--------------------------------------------------------------------------------
-- Appearance
--------------------------------------------------------------------------------
config.color_scheme = "Tokyo Night"
config.font = wezterm.font_with_fallback({
	"JetBrains Mono",
	"Menlo",
})
config.font_size = 13.0
config.line_height = 1.1

config.window_background_opacity = 0.98
config.macos_window_background_blur = 20
config.window_decorations = "RESIZE"
config.window_padding = {
	left = 8,
	right = 8,
	top = 8,
	bottom = 8,
}

-- Auto-resize the window when the available screen space changes (e.g., when
-- unplugging an external monitor). WezTerm adjusts the window to fit the new
-- screen dimensions rather than staying at the old fixed size.
config.adjust_window_size_when_changing_font_size = true
config.window_close_confirmation = "NeverPrompt"

-- Set initial window dimensions to reasonable defaults that work on most
-- screens (will be overridden if you've explicitly sized the window before).
-- When a screen disconnects, WezTerm will respect the available space on the
-- remaining screen(s) rather than forcing the old size.
config.initial_cols = 220
config.initial_rows = 50

--------------------------------------------------------------------------------
-- Tabs
--------------------------------------------------------------------------------
config.enable_tab_bar = true
config.hide_tab_bar_if_only_one_tab = true
config.use_fancy_tab_bar = true
config.tab_bar_at_bottom = false
config.tab_max_width = 32

--------------------------------------------------------------------------------
-- Behavior
--------------------------------------------------------------------------------
config.scrollback_lines = 10000
config.audible_bell = "Disabled"
config.default_cursor_style = "SteadyBar"
config.check_for_updates = false
config.automatically_reload_config = true

--------------------------------------------------------------------------------
-- Key bindings
--------------------------------------------------------------------------------
config.keys = {
	-- Tabs: switch left / right
	{ key = "LeftArrow", mods = "CMD", action = act.ActivateTabRelative(-1) },
	{ key = "RightArrow", mods = "CMD", action = act.ActivateTabRelative(1) },

	-- Tabs: move (reorder) current tab left / right
	{ key = "LeftArrow", mods = "CMD|SHIFT", action = act.MoveTabRelative(-1) },
	{ key = "RightArrow", mods = "CMD|SHIFT", action = act.MoveTabRelative(1) },

	-- Tabs: new (always opens in the home directory, not the current pane's cwd)
	{ key = "t", mods = "CMD", action = act.SpawnCommandInNewTab({ cwd = wezterm.home_dir }) },
	{ key = "w", mods = "CMD", action = act.CloseCurrentTab({ confirm = true }) },

	-- Tabs: rename the current tab (inline prompt at the bottom of the window)
	{
		key = "e",
		mods = "CMD|SHIFT",
		action = act.PromptInputLine({
			description = "Rename tab:",
			action = wezterm.action_callback(function(window, _, line)
				-- line is nil if the prompt was cancelled with Esc.
				if line ~= nil then
					window:active_tab():set_title(line)
				end
			end),
		}),
	},

	-- Panes: split horizontally / vertically
	{ key = "d", mods = "CMD", action = act.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
	{ key = "d", mods = "CMD|SHIFT", action = act.SplitVertical({ domain = "CurrentPaneDomain" }) },

	-- Panes: navigate with Cmd+Alt+Arrow
	{ key = "LeftArrow", mods = "CMD|ALT", action = act.ActivatePaneDirection("Left") },
	{ key = "RightArrow", mods = "CMD|ALT", action = act.ActivatePaneDirection("Right") },
	{ key = "UpArrow", mods = "CMD|ALT", action = act.ActivatePaneDirection("Up") },
	{ key = "DownArrow", mods = "CMD|ALT", action = act.ActivatePaneDirection("Down") },

	-- Panes: close current pane
	{ key = "w", mods = "CMD|SHIFT", action = act.CloseCurrentPane({ confirm = true }) },

	-- Font size
	{ key = "=", mods = "CMD", action = act.IncreaseFontSize },
	{ key = "-", mods = "CMD", action = act.DecreaseFontSize },
	{ key = "0", mods = "CMD", action = act.ResetFontSize },

	-- Clipboard
	-- Cmd+C: explicitly read the current selection and copy it to the clipboard.
	-- Does nothing when there is no selection (normal macOS Cmd+C behavior).
	{
		key = "c",
		mods = "CMD",
		action = wezterm.action_callback(function(window, pane)
			local sel = window:get_selection_text_for_pane(pane)
			if sel and sel ~= "" then
				window:copy_to_clipboard(sel, "Clipboard")
			end
		end),
	},
	{ key = "v", mods = "CMD", action = act.PasteFrom("Clipboard") },
}

--------------------------------------------------------------------------------
-- Mouse
--------------------------------------------------------------------------------
-- Don't auto-copy on select. The mouse-release does Nop (nothing), so no
-- selection is ever routed to a clipboard buffer. The drag still creates and
-- highlights the selection; nothing lands on the clipboard until you press
-- Cmd+C, which explicitly reads the highlighted selection (see the Cmd+C
-- binding above). Nop is used instead of CompleteSelection("PrimarySelection")
-- because on macOS the primary selection is aliased to the clipboard, so
-- completing into it was still auto-copying.
--
-- Because plain click no longer opens hyperlinks, Ctrl+click is bound for that.
config.mouse_bindings = {
	{
		event = { Up = { streak = 1, button = "Left" } },
		mods = "NONE",
		action = act.Nop,
	},
	-- Double / triple click select words / lines without copying either.
	{
		event = { Up = { streak = 2, button = "Left" } },
		mods = "NONE",
		action = act.Nop,
	},
	{
		event = { Up = { streak = 3, button = "Left" } },
		mods = "NONE",
		action = act.Nop,
	},
	-- Ctrl+click opens hyperlinks (plain click no longer does).
	{
		event = { Up = { streak = 1, button = "Left" } },
		mods = "CTRL",
		action = act.OpenLinkAtMouseCursor,
	},
}

-- Cmd+1 .. Cmd+9 to jump directly to a tab by index
for i = 1, 9 do
	table.insert(config.keys, {
		key = tostring(i),
		mods = "CMD",
		action = act.ActivateTab(i - 1),
	})
end

--------------------------------------------------------------------------------
-- Tab activity indicator (iTerm2-style running / done / idle dot)
--------------------------------------------------------------------------------
-- The terminal can only see a tab's foreground *process*. That works for plain
-- commands, but a long-lived TUI app (Claude Code, vim, a REPL) stays the
-- foreground process the whole session, so "process is running" is true from
-- launch to quit and never reflects whether the app is busy or waiting on you.
--
-- The one thing an app emits when it finishes a turn and wants attention is the
-- terminal bell. We hook the `bell` event to flip the tab to a green "done"
-- dot, and clear it again once you focus that tab.
--
-- Shells that count as "at the prompt" (idle). If the tab's foreground process
-- is one of these, nothing is running; anything else means a command is active.
local SHELLS = {
	["zsh"] = true,
	["bash"] = true,
	["fish"] = true,
	["sh"] = true,
	["-zsh"] = true,
	["-bash"] = true,
}

local RUNNING_DOT = "●" -- solid: a command / app is running in this tab
local DONE_DOT = "●" -- solid: rang the bell = finished, wants your attention
local IDLE_DOT = "○" -- hollow: sitting at the prompt (idle)

-- Colors tuned for the Tokyo Night scheme.
local RUNNING_COLOR = "#e0af68" -- amber while running
local DONE_COLOR = "#9ece6a" -- green: done / needs attention (bell fired)
local IDLE_COLOR = "#565f89" -- dim: idle

-- Panes that have rung the bell and not yet been looked at. Persisted in
-- wezterm.GLOBAL so it survives config reloads. Keyed by pane id (as string).
local function set_done(pane_id, value)
	local t = wezterm.GLOBAL.done_panes or {}
	t[tostring(pane_id)] = value or nil
	wezterm.GLOBAL.done_panes = t
end

local function is_done(pane_id)
	local t = wezterm.GLOBAL.done_panes or {}
	return t[tostring(pane_id)] == true
end

-- Bell fired in a pane -> mark it "done / needs attention".
wezterm.on("bell", function(_, pane)
	set_done(pane:pane_id(), true)
end)

-- The currently focused pane can't be "unseen" -> clear its done flag.
-- Background tabs are untouched, so their green dot persists until you switch
-- to them. Fires on focus changes and periodic status updates.
wezterm.on("update-status", function(_, pane)
	if pane then
		set_done(pane:pane_id(), false)
	end
end)

local function basename(path)
	if not path then
		return ""
	end
	return path:gsub("(.*[/\\])(.*)", "%2")
end

wezterm.on("format-tab-title", function(tab, tabs, panes, conf, hover, max_width)
	local pane = tab.active_pane
	local proc = basename(pane.foreground_process_name)

	local dot, dot_color
	if is_done(pane.pane_id) then
		-- Bell fired here and you haven't looked yet.
		dot, dot_color = DONE_DOT, DONE_COLOR
	elseif proc ~= "" and not SHELLS[proc] then
		dot, dot_color = RUNNING_DOT, RUNNING_COLOR
	else
		dot, dot_color = IDLE_DOT, IDLE_COLOR
	end

	-- Title: prefer the tab's own title, else the foreground process name.
	local title = tab.tab_title
	if not title or #title == 0 then
		title = proc ~= "" and proc or "shell"
	end

	-- Leave room for the dot, a space, and the tab index.
	local prefix = string.format(" %d: ", tab.tab_index + 1)
	local budget = max_width - #prefix - 3
	if #title > budget and budget > 1 then
		title = title:sub(1, budget - 1) .. "…"
	end

	return {
		{ Text = prefix },
		{ Foreground = { Color = dot_color } },
		{ Text = dot .. " " },
		{ Foreground = { Color = "#c0caf5" } },
		{ Text = title .. " " },
	}
end)

return config
