# RESOURCES

## Useful Resources:
- https://www.flaticon.com/
    - For generating geometric figures with simple backgrounds
- https://image-sonification.vercel.app/
    - Cool trap music-like (hi-hats, bass, drums) image-convertor
- todo
    - todo
    
## Ideas 
- Depth Maps - closer objects are more whiter - so they sound louder - Can give people a feeling of "Distance'
-  

## Articles:
- https://www.researchgate.net/figure/Conversion-of-image-to-sound-using-The-vOICe-algorithm-White-pixels-in-the-image-are_fig1_259355334 (accesat pe 4 Mai)
    - Image calibration idea was from **1. Introduction - 2. Stimulus Design**
    - Has cool pictures

- https://www.nature.com/articles/s41539-025-00385-4 (accesat pe 6 Mai)
    - The research shows that people can learn to "hear" images in under 30 minutes, performing just as well whether the app uses the standard layout (**X - time, Y - pitch**) or a flipped one (**X - pitch, Y - time**).
    - This shows that **our brains are very adaptable**: users learn to "hear" images based on consistent, predictable rules in the app, rather than relying on natural instincts.

- https://dl.acm.org/doi/abs/10.1145/2818346.2823298 (accesat pe 6 Mai)
    - The study strongly validates the **WASD Explorer concept**, proving that interactive, cursor-based exploration allows even untrained users to recognize shapes and navigate with over 80% accuracy.
    - It highlights that *active sonification* is **highly intuitive** for **real-world tasks** (like *reading graphs* or *floor maps*) and justifies using **computer vision** (OpenCV) to pre-process images for clearer audio feedback.
    - The justification for using computer vision is from ***2. System***, and the accuracy data on real-world tasks is from ***3. Experiments***.

- https://pub.uni-bielefeld.de/record/2017438 (accesat pe 6 Mai)
    - **Humans naturally learn by actively exploring their environment**. If you hear *an entire image sonified* all at once, it can be *overwhelming and confusing*. But if you explore it **systematically** (like using ***WASD keys***), your brain can easily figure out the shapes.

    - It introduces the **"sensor-actor loop"**, which proves that getting **instant audio feedback** the moment you press a key is the *most natural way* to understand spatial data.

    - The core ideas about human exploration and the sensor-actor loop are from ***2. The Role of Interaction in Real-World Contexts - 2.3 Co-ordination & 2.4 Learning***.
- https://doi.org/10.3390/s20113222 (accesat pe 8 Mai)
    - The study proves that converting raw image data into sound causes **cognitive overload**. Flooding the ear with too much detail (like 256 grayscale levels) simply overwhelms and blocks the brain.

    - This perfectly justifies our use of **K-Means Clustering**. By reducing the visual noise to just 4 distinct audio levels, we prevent mental fatigue while keeping the core shapes clear.
    
    - The findings on cognitive burden and the need for data simplification are directly drawn from ***5.3. Complexity*** and ***6. Conclusions***.
- https://doi.org/10.1152/jn.00104.1999 (accesat pe 8 Mai)
    - The auditory cortex evaluates pitch differences as percentages (Weber fractions) rather than absolute values. A 10 Hz change is obvious at low frequencies but imperceptible at high frequencies, perfectly mirroring a **logarithmic curve**.

    - This proves why `np.geomspace` is vital: it scales frequencies logarithmically so that moving the cursor by one pixel always produces the exact same perceived pitch shift, regardless of the cursor's vertical position.

    - The brain's reliance on relative frequency scaling (Weber fractions) and non-linear tuning is drawn from ***RESULTS - Frequency direction discrimination*** and ***DISCUSSION - Physiological considerations***.

- https://doi.org/10.1177/1059712313497975 (accesat pe 8 Mai)
    - The article discusses **Sensorimotor Contingency Theory (SMCT)**, arguing that perception is not passive, but an active exploration process. This perfectly validates the **WASD Explorer** mode, where users mentally map the image by taking active steps and hearing the resulting changes.

    - The research highlights that any delay between a physical action and its sensory feedback severely disrupts the brain's ability to learn. This proves the critical necessity of our **Multithreading architecture**, which eliminates UI-audio lag and provides the instant feedback required for the sensorimotor loop.

    - The importance of active exploration is drawn from ***1. Introduction***, while the disruptive effect of action-to-feedback delays (latency/inertia) is analyzed in ***3.4 Robotic hardware and experimental setup***.

## Main Documentation 

- https://customtkinter.tomschimansky.com/
    -  CustomTkinter - Useful for GUI
