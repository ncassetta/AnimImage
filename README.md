# AnimImage
Animated sprites for pygame

AnimImage is a set of Python 3 classes written by Nicola Cassetta, implementing animated sprites to be used within the pygame library (see https://www.pygame.org). There are various types of animations:

+ **AnimSprite** an animated Sprite class. The user must set a list of frames (pygame Surface) which will be shown in sequence; moreover he can choose between a one-shot animation (the Sprite will disappear at the end of the sequence) or a looped one.
+ **VanishSprite** a vanishing Sprite class. Starting from a given image (pygame Surface) it generates a list of frames with increasing transparence which will be shown in sequence, giving the impression of a disappearing image. Moreover the image can change its dimensions (growing or shrinking) and move in a fixed direction during the animation.
+ **FlashSprite** a flashing Sprite class. Starting from a given image (pygame Surface) it shows and hides it for a given number of times. After them you can mantain the Sprite shown or kill it.

All three classes allow the user to control the rate of the animation and to stop and restart it. They are subclasses of the Sprite object, so they can be added and deleted to pygame groups via usual methods. Their use is similar to that of pygame Sprites:
+ the constructor allows the user to add the object to one or more groups;
+ after creating the object you need to call another method which defines the *image* and *rect* attributes of the Sprite. This method also starts drawing the object;
+ the *update()* method is used in all three classes to make the animation progress, so when subclassing them remember, if you subclass update(), to call the base class method.

AnimImage includes also **GIFDecoder**, an object which splits an animated GIF file into its frames and **SheetSlicer**, an object which separates the various images of a big frameset into separated Surface objects.
