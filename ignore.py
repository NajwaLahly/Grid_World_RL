import pygame

pygame.init()
pygame.display.set_mode((200, 200))
SCREEN=pygame.display.set_mode((2, 2))
pygame.display.set_caption("GridWorld")
print("a")
rect = pygame.Rect(1, 2,
                               3, 3)
pygame.draw.rect(SCREEN, (200, 200, 200), rect, 1)
while self.running:
    self.drawGrid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            # sys.exit()
