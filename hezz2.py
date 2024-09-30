import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hezz2 Game")

# Colors
BACKGROUND = (240, 230, 220)
TEXT_COLOR = (50, 50, 50)
BUTTON_COLOR = (200, 180, 160)
BUTTON_HOVER_COLOR = (180, 160, 140)
HIGHLIGHT_COLOR = (255, 215, 0)

# Card dimensions
CARD_WIDTH = 100
CARD_HEIGHT = 150

# Load background image
background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.image = pygame.image.load(f"Carte-game/{suit}/{value}-{suit}.png")
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = []
        self.is_ai = is_ai

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=10)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()

class Hezz2Game:
    def __init__(self):
        self.suits = ['Bastos', 'Copas', 'Espadas', 'Oros']
        self.values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.players = [Player("Player"), Player("AI", is_ai=True)]
        self.deck = self.create_deck()
        self.center_card = None
        self.current_player = 0
        self.draw_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 100, 40, "Draw Card", self.draw_card)
        self.message = ""
        self.selecting_suit = False
        self.suit_buttons = [
            Button(SCREEN_WIDTH//2 - 220 + i*110, SCREEN_HEIGHT//2 + 100, 100, 40, suit, lambda s=suit: self.select_suit(s))
            for i, suit in enumerate(self.suits)
        ]
        self.card_back = pygame.image.load("card_back.png")
        self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))

    def create_deck(self):
        deck = [Card(suit, value) for suit in self.suits for value in self.values]
        random.shuffle(deck)
        return deck

    def deal_cards(self):
        for _ in range(4):
            for player in self.players:
                player.hand.append(self.deck.pop())
        self.center_card = self.deck.pop()

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def play_card(self, card_index):
        player = self.players[self.current_player]
        card = player.hand[card_index]
        
        if card.suit == self.center_card.suit or card.value == self.center_card.value:
            played_card = player.hand.pop(card_index)
            self.center_card = played_card
            
            if card.value == 1:
                self.next_player()
                self.message = f"{player.name} played a 1. Skipping next player's turn!"
            elif card.value == 2:
                next_player = self.players[(self.current_player + 1) % len(self.players)]
                next_player.hand.append(self.deck.pop())
                next_player.hand.append(self.deck.pop())
                self.message = f"{player.name} played a 2. Next player draws 2 cards!"
            elif card.value == 7:
                if player.is_ai:
                    self.select_suit(random.choice(self.suits))
                else:
                    self.selecting_suit = True
                    self.message = f"{player.name} played a 7. Select a new suit!"
                return True
            else:
                self.message = f"{player.name} played {card.value} of {card.suit}"
            
            if not self.selecting_suit:
                self.next_player()
            return True
        return False

    def select_suit(self, suit):
        self.center_card.suit = suit
        self.message = f"Changing suit to {suit}!"
        self.selecting_suit = False
        self.next_player()

    def draw_card(self):
        if self.deck:
            drawn_card = self.deck.pop()
            self.players[self.current_player].hand.append(drawn_card)
            self.message = f"{self.players[self.current_player].name} drew a card"
            
            # Only show the drawn card briefly if it's the AI's turn
            if self.players[self.current_player].is_ai:
                self.draw_game(show_ai_card=drawn_card)
                pygame.display.flip()
                pygame.time.wait(500)  # Show for 500 milliseconds
            
            self.next_player()

    def ai_play(self):
        ai_player = self.players[self.current_player]
        playable_cards = [i for i, card in enumerate(ai_player.hand) 
                          if card.suit == self.center_card.suit or card.value == self.center_card.value]
        
        if playable_cards:
            card_index = random.choice(playable_cards)
            self.play_card(card_index)
        else:
            self.draw_card()

    def draw_game(self, show_ai_card=None):
        screen.blit(background_image, (0, 0))
        
        # Draw center card
        center_x = SCREEN_WIDTH // 2 - CARD_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (center_x-5, center_y-5, CARD_WIDTH+10, CARD_HEIGHT+10), border_radius=10)
        screen.blit(self.center_card.image, (center_x, center_y))
        
        # Draw player's hand
        player = self.players[0]  # Human player
        for i, card in enumerate(player.hand):
            x = 50 + i * (CARD_WIDTH + 10)
            y = SCREEN_HEIGHT - CARD_HEIGHT - 50
            screen.blit(card.image, (x, y))
        
        # Draw AI's hand (face down)
        ai_player = self.players[1]
        for i in range(len(ai_player.hand)):
            x = 50 + i * (CARD_WIDTH + 10)
            y = 50
            screen.blit(self.card_back, (x, y))
        
        # Draw text
        font = pygame.font.Font(None, 36)
        current_player = self.players[self.current_player]
        text = font.render(f"{current_player.name}'s turn", True, TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.right = SCREEN_WIDTH - 20
        text_rect.top = 20
        screen.blit(text, text_rect)
        
        # Draw message
        message_font = pygame.font.Font(None, 24)
        message_text = message_font.render(self.message, True, TEXT_COLOR)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(message_text, message_rect)
        
        # Draw button
        self.draw_button.draw(screen)
        
        # Draw suit selection buttons if selecting suit
        if self.selecting_suit:
            for button in self.suit_buttons:
                button.draw(screen)

def main():
    game = Hezz2Game()
    game.deal_cards()
    
    running = True
    while running:
        game.draw_game()
        pygame.display.flip()
        
        if game.players[game.current_player].is_ai:
            time.sleep(1)  # Add a delay to make AI turns visible
            game.ai_play()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if SCREEN_HEIGHT - CARD_HEIGHT - 50 < y < SCREEN_HEIGHT - 50:
                        card_index = (x - 50) // (CARD_WIDTH + 10)
                        if 0 <= card_index < len(game.players[game.current_player].hand):
                            game.play_card(card_index)
                    game.draw_button.handle_event(event)
                    if game.selecting_suit:
                        for button in game.suit_buttons:
                            button.handle_event(event)
                else:
                    game.draw_button.handle_event(event)
                    if game.selecting_suit:
                        for button in game.suit_buttons:
                            button.handle_event(event)
        
        pygame.display.flip()
        
        if any(not player.hand for player in game.players):
            winner = next(player for player in game.players if not player.hand)
            print(f"{winner.name} wins!")
            running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()