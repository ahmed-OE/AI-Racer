import sys
import pygame
import random
from car import Car
from track_drawer import Track
from Model import agent_step, group_train_step, save_model, load_model
import Model as ai

pygame.init()
WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI-Racer (50 Cars)")
clock = pygame.time.Clock()
FPS = 60
reward_drawn = False
drawing_drift = True
Track_size = 45
Track_Draw_mode = "Track"

track = Track(width=WIDTH, height=HEIGHT)

all_lap_times = []


NUM_CARS = 50

Car_COLOR = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(255, 255, 0),(255, 0, 255)]

cars = [Car(track.spawn_car_x, track.spawn_car_y, random.choice(Car_COLOR)) for _ in range(NUM_CARS)]

state = "DRAW"
draw_edit = False          
training_mode = False   
toggle_rays = 0
frame_count = 0


font = pygame.font.SysFont("Arial", 16)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                save_model()
            if event.key == pygame.K_l:
                load_model()

            if event.key == pygame.K_m:
                if state == "DRAW":
                    state = "DRIVE"
                    cars = [Car(track.spawn_car_x, track.spawn_car_y, random.choice(Car_COLOR))]
                    training_mode = False
                else:
                    state = "DRAW"

            if event.key == pygame.K_i:
                toggle_rays = 1 - toggle_rays

            if event.key == pygame.K_p:
                print("All lap times:", all_lap_times)
                for i, car in enumerate(cars):
                    print(f"Car {i} lap times: {car.lap_times}")

            if state == "DRAW":

                if event.key == pygame.K_e:
                    if draw_edit == True:
                        draw_edit = False
                    else:
                        draw_edit = True 

                if draw_edit:
                    if event.type == pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_1:
                                if Track_Draw_mode == "Track" or Track_Draw_mode == "Drift-D" or Track_Draw_mode == "Drift-C":
                                    Track_Draw_mode = "Track"
                                    Track_size = 50
                                    track.clear()
                                    track.checkpoints.clear()
                                    reward_drawn = False
                            case pygame.K_2:
                                if Track_Draw_mode == "Track" or Track_Draw_mode == "Drift-D" or Track_Draw_mode == "Drift-C":
                                    Track_Draw_mode = "Track"
                                    Track_size = 45
                                    track.clear()
                                    track.checkpoints.clear()
                                    reward_drawn = False
                            case pygame.K_3:
                                if Track_Draw_mode == "Track" or Track_Draw_mode == "Drift-D" or Track_Draw_mode == "Drift-C":
                                    Track_Draw_mode = "Track"
                                    Track_size = 35
                                    track.clear()
                                    track.checkpoints.clear()
                                    reward_drawn = False
                            case pygame.K_4:
                                reward_drawn = False
                                Track_Draw_mode = "Track"
                                curr_mouse_pos = pygame.mouse.get_pos()
                                track.checkpoints.clear()
                                track.checkpoints.append((1, [track.spawn_car_x, track.spawn_car_y]))
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    pygame.draw.circle(screen,(100, 100, 100),(curr_mouse_pos), Track_size * 0.90)
                                    
                            case pygame.K_5:  
                                reward_drawn = False
                                Track_Draw_mode = "Drift-D"

                            case pygame.K_6:
                                reward_drawn = False
                                Track_Draw_mode = "Drift-C"

                            case pygame.K_0:
                                track.checkpoints.clear()
                                track.checkpoints.append((1, [track.spawn_car_x, track.spawn_car_y]))
                                reward_drawn = False
                                        
                
                if event.key == pygame.K_c:
                    track.clear()
                    track.checkpoints.clear()
                    reward_drawn = False


            
            if event.key == pygame.K_t and state == "DRIVE":
                if event.key == pygame.K_t and state == "DRIVE":
                    training_mode = not training_mode
                    if training_mode:
                        print("Training ON")
                        cars = [Car(track.spawn_car_x, track.spawn_car_y, random.choice(Car_COLOR)) for _ in range(NUM_CARS)]
                    else:
                        print("Manual ON")
                        cars = [Car(track.spawn_car_x, track.spawn_car_y, random.choice(Car_COLOR))] 

        if state == "DRAW":
            track.handle_event(event)

    # ---------- UPDATE ----------
    if state == "DRAW":
        track.update(Track_size, Track_Draw_mode)

    elif state == "DRIVE":
        if training_mode:
            # 1. Let every car act and learn
            for c in cars:
                agent_step(c, track)
            # 2. Update the neural network once per frame
            group_train_step()

            frame_count += 1
            if frame_count % 2000 == 0:
                print(f"[frame {frame_count}] epsilon={ai.epsilon:.3f} "
                      f"buffer={len(ai.replay_buffer)} step={ai.step_count}")
                save_model()

        else:   # manual mode (training_mode == False)
    
            cars[0].handle_input()
            for c in cars:
                c.update()
                c.rays(track.surface)
                c.is_in_drift_zone = track.is_on_drift_zone(c)
                dt = clock.get_time() / 1000.0
                c.update_drift_boost(dt)


                if track.is_off_track(c):
                    c.reset(track.spawn_car_x, track.spawn_car_y)  
                    continue   

  
                if c.left_start and track.is_on_finish_line(c) and c.speed > 0.5:
                    if not c.finished:
                        lap_time = c.get_elapsed()
                        c.lap_times.append(lap_time)
                        all_lap_times.append(lap_time)  
                        c.lap_start_time = pygame.time.get_ticks() 
                        print(f"Manual lap: {lap_time:.2f}s")
                    c.finished = True
                else:
                    c.finished = False
                        



    # ---------- DRAW ----------
    screen.fill((0, 0, 0))
    track.draw(screen)

    if reward_drawn != True:
        for number, position in track.checkpoints:
            if number == 1:
                pass
            else:
                pygame.draw.circle(screen,(100, 100, 100),(int(position.x), int(position.y)), Track_size * 0.90)
      
                        

    if state == "DRIVE":
        # Draw all 50 cars
        for c in cars:
            screen.blit(c.image, c.rect)
          
        # Draw rays ONLY for the first car to avoid massive screen clutter
        if toggle_rays == 1:
            for start, end in cars[0].rays_cords:
                pygame.draw.line(screen, (255, 255, 0), start, end, 2)
            for _, end in cars[0].rays_cords:
                pygame.draw.circle(screen, (255, 0, 0), (int(end.x), int(end.y)), 4)

    # UI
    if state == "DRAW":

        if draw_edit == False:
            banner_text = "DRAW: Draw track | C: Clear | M: Drive | E: Toggle Edit" 
            banner_color = (0, 255, 128)
        else:
            banner_text = "DRAW Options: | (1): Large brush | (2): Medium brush | (3): Small brush | (4): Checkpoint | (5): Drift-zone | (6): Clear dirft-zone (Draw)| (0): Clear checkpoints | C: Clear all | E: Toggle Edit" 
            banner_color = (0, 255, 128)
    else:
        mode_text = "TRAINING (50 CARS)" if training_mode else "MANUAL (1 CAR)"
        banner_text = f"DRIVE: {mode_text} | T: toggle AI | M: Edit | I: toggle Rays | K/L: Save/Load"
        banner_color = (255, 200, 0)

    text_surface = font.render(banner_text, True, banner_color)
    screen.blit(text_surface, (20, 20))

    pygame.display.flip()

    if state == "DRIVE" and training_mode:
        clock.tick(0)   # uncapped: pump as many training steps/sec as possible
    else:
        clock.tick(FPS)

pygame.quit()
sys.exit()