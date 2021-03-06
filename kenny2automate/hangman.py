import asyncio as a
import discord as d
from discord.ext.commands import command
from discord.ext.commands import bot_has_permissions
from discord.ext import commands as c
from .i18n import i18n

DGHANGMANSHANPES = [
	'```\n_\n\n\n\n_```',
	'```\n_\n\n\n\u2500\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502\n\u2502\n\u2502\n\u2514\u2500\
\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502\n\u2502\n\u2514\
\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502  /\n\u2502\n\u2514\
\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502  / \\\n\u2502\n\
\u2514\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502  /|\\\n\u2502\n\
\u2514\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502  /|\\\n\u2502  /\n\
\u2514\u2500\u2500\u2500\u2500\n```',
	'```\n\u250c\u2500\u2500\u2500\u2510\n\u2502   O\n\u2502  /|\\\n\u2502  / \
\\\n\u2514\u2500\u2500\u2500\u2500\n```'
]

class Hangman(object):
	def __init__(self, bot, logger ,db):
		self.bot = bot
		self.logger = logger
		self.db = db

	@staticmethod
	def substrs(sub, string):
		last_found = -1
		while 1:
			last_found = string.lower().find(sub, last_found + 1)
			if last_found == -1:
				break
			yield last_found

	@command()
	@c.check(lambda ctx: \
		ctx.guild \
		and (not ctx.channel.permissions_for(ctx.guild.me).manage_messages)
	)
	async def crudehangman(self, ctx):
		"""Hangman for less permissions

		Use this first in the server, to start the game in that channel;
		Next, send the word in a DM with the bot, to set it.
		Once that's been done, guess a letter by sending it.
		"""
		self.logger.info('Games.crudehangman', extra={'ctx': ctx})
		res = self.db.execute(
			'SELECT ch_occupied FROM channels WHERE channel_id=?',
			(ctx.channel.id,)
		).fetchone()
		if res is not None and not res['ch_occupied']:
			await ctx.send(i18n(ctx, 'hangman/crudehangman-occupied'))
			ownerq = await self.bot.is_owner(ctx.author)
			if not ownerq:
				return
		if res is None:
			self.db.execute(
				'INSERT INTO channels (channel_id, ch_occupied) VALUES (?, 1)',
				(ctx.channel.id,)
			)
		else:
			self.db.execute(
				'UPDATE channels SET ch_occupied=1 WHERE channel_id=',
				(ctx.channel.id,)
			)
		await ctx.send(i18n(ctx, 'hangman/awaiting-dm'))
		try:
			msg = await ctx.bot.wait_for('message',
				check=lambda m: \
					isinstance(m.channel, d.DMChannel) \
					and m.author == ctx.author,
				timeout=60.0)
		except a.TimeoutError:
			await ctx.send(i18n(ctx, 'hangman/timeout'))
			return
		WORD = msg.content
		letters = ['_'] * len(WORD)
		lowers = (
			'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
			'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
			'u', 'v', 'w', 'x', 'y', 'z'
		)
		for i in range(len(WORD)):
			if WORD[i].lower() not in lowers:
				letters[i] = WORD[i]
		missed = []
		shanpe = 0
		await ctx.send(i18n(
			ctx, 'hangman/main', DGHANGMANSHANPES[shanpe], "", "".join(letters)
		))
		while "".join(letters) != WORD and shanpe < len(DGHANGMANSHANPES) - 1:
			letter = (await ctx.bot.wait_for('message',
				check=lambda m: \
					m.channel == ctx.channel \
					and m.content in lowers)
			).content
			if WORD.lower().find(letter) != -1:
				for i in self.substrs(letter, WORD):
					letters[i] = WORD[i]
			else:
				if letter not in missed:
					missed.append(letter)
					shanpe += 1
			await ctx.send(i18n(
				ctx, 'hangman/main', DGHANGMANSHANPES[shanpe],
				i18n(ctx, 'hangman/comma-sep').join(missed), "".join(letters)
			))
		if "".join(letters) == WORD:
			await ctx.send(i18n(ctx, 'hangman/won'))
		else:
			await ctx.send(i18n(ctx, 'hangman/lost', WORD))
		self.db.execute(
			'UPDATE channels SET ch_occupied=0 WHERE channel_id=?',
			(ctx.channel.id,)
		)

	@command()
	@bot_has_permissions(
		manage_messages=True, add_reactions=True, read_message_history=True
	)
	async def hangman(self, ctx):
		"""Hangman!

		Use this in the channel to start the game there,
		DM the bot the word to set it
		then send letters to guess them.
		Requires the "Manage Messages" permission.
		"""
		REGS = '\U0001f1e6 \U0001f1e7 \U0001f1e8 \U0001f1e9 \U0001f1ea \
\U0001f1eb \U0001f1ec \U0001f1ed \U0001f1ee \U0001f1ef \U0001f1f0 \U0001f1f1 \
\U0001f1f2 \U0001f1f3 \U0001f1f4 \U0001f1f5 \U0001f1f6 \U0001f1f7 \U0001f1f8 \
\U0001f1f9 \U0001f1fa \U0001f1fb \U0001f1fc \U0001f1fd \U0001f1fe \U0001f1ff' \
.split(' ')
		REGS1, REGS2 = REGS[:13], REGS[13:]
		NEIN = '\u274c'
		self.logger.info('Games.hangman', extra={'ctx': ctx})
		await ctx.send(i18n(ctx, 'hangman/awaiting-dm'))
		try:
			msg = await ctx.bot.wait_for('message',
				check=lambda m: \
					isinstance(m.channel, d.DMChannel) \
					and m.author == ctx.author,
				timeout=60.0)
		except a.TimeoutError:
			await ctx.send(i18n(ctx, 'hangman/timeout'))
			return
		WORD = msg.content
		letters = ['_'] * len(WORD)
		lowers = (
			'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
			'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
			'w', 'x', 'y', 'z'
		)
		translate = {}
		for regn in range(len(REGS)):
			translate[REGS[regn]] = lowers[regn]
		for i in range(len(WORD)):
			if WORD[i].lower() not in lowers:
				letters[i] = WORD[i]
		missed = []
		shanpe = 0
		status = await ctx.send(i18n(
			ctx, 'hangman/main', DGHANGMANSHANPES[shanpe],
			i18n(ctx, 'hangman/comma-sep').join(missed),
			"".join(letters),
			'\n**{}**'.format(
				i18n(ctx, 'hangman/wait')
			)
		))
		reactionmsg1 = await ctx.send('_ _')
		reactionmsg2 = await ctx.send('_ _')
		await status.add_reaction(NEIN)
		for reg in REGS1:
			await reactionmsg1.add_reaction(reg)
		for reg in REGS2:
			await reactionmsg2.add_reaction(reg)
		await status.edit(content=status.content[:-25])
		while "".join(letters) != WORD and shanpe < len(DGHANGMANSHANPES) - 1:
			try:
				reaction, user = await ctx.bot.wait_for(
					'reaction_add',
					check=lambda r, u: \
						r.message.id in (status.id, reactionmsg1.id, reactionmsg2.id) \
						and str(r) in REGS + [NEIN] \
						and u.id != self.bot.user.id,
					timeout=600.0
				)
			except a.TimeoutError:
				await status.edit(content=i18n(ctx, 'hangman/timeout2'))
				await status.clear_reactions()
				await reactionmsg1.delete()
				await reactionmsg2.delete()
				return
			if str(reaction) == NEIN:
				if user.id == ctx.author.id:
					await status.edit(
						content=i18n(ctx, 'pm_games/game-cancelled')
					)
					await status.clear_reactions()
					await reactionmsg1.delete()
					await reactionmsg2.delete()
					return
				else:
					continue
			else:
				letter = translate[str(reaction)]
			await reaction.message.remove_reaction(reaction, user)
			if WORD.lower().find(letter) != -1:
				for i in self.substrs(letter, WORD):
					letters[i] = WORD[i]
			else:
				if letter not in missed:
					missed.append(letter)
					shanpe += 1
			await status.edit(content=i18n(
				ctx, 'hangman/main', DGHANGMANSHANPES[shanpe],
				i18n(ctx, 'hangman/comma-sep').join(missed),
				"".join(letters),
				""
			))
		if "".join(letters) == WORD:
			await ctx.send(i18n(ctx, 'hangman/won'))
		else:
			await ctx.send(i18n(ctx, 'hangman/lost', WORD))
