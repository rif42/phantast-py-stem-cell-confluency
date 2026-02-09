# **Advanced Computational Frameworks for Phase Contrast Microscopy: A Comprehensive Technical Analysis of PHANTAST**

The quantitative assessment of adherent cell cultures is a foundational requirement in modern biotechnology, regenerative medicine, and drug discovery. Among the metrics utilized to evaluate culture health and progression, confluency—defined as the percentage of a growth surface covered by adherent cells—serves as a critical proxy for proliferation, metabolic activity, and the timing of experimental interventions.1 Traditionally, this measurement relied on the qualitative "guesstimation" of researchers, a process fraught with inter-operator variability and subjective bias.1 The Phase-contrast Microscopy Segmentation Toolbox (PHANTAST) was developed to address this methodological gap by providing an automated, precise, and non-invasive means of estimating cell culture characteristics directly from unlabeled phase contrast microscopy (PCM) images.4

Developed at University College London’s Department of Biochemical Engineering and CoMPLEX, PHANTAST represents a shift toward open-source, high-performance image processing specifically tuned to the optical complexities of PCM.4 Unlike standard brightfield or fluorescence imaging, PCM introduces unique artifacts, such as the halo effect and shade-off, which historically rendered simple intensity-based thresholding ineffective.7 PHANTAST overcomes these challenges through a dual-stage algorithmic architecture combining local contrast thresholding with a post-hoc gradient correction, enabling rapid processing that integrates seamlessly into professional laboratory workflows.8

## **Optical Physics and the Computational Challenges of Phase Contrast Microscopy**

To understand the operational logic of PHANTAST, one must first consider the physical interactions between light and biological specimens that produce a PCM image. Phase contrast microscopy, pioneered by Frits Zernike, is designed to visualize transparent "phase objects" such as living cells without the need for destructive staining.2 Cells typically possess a higher refractive index than their surrounding aqueous media, causing a phase shift in the light passing through them. The PCM optical system converts these phase shifts into amplitude variations, making the cells appear as darker or lighter structures against a neutral background.8

However, this transformation introduces significant image processing obstacles. The two most prominent artifacts are the halo effect and the shade-off effect.10 The halo effect appears as a bright, luminous perimeter surrounding cellular objects, caused by the diffraction of light at the cell edges and its subsequent modulation by the phase ring in the objective lens.7 Shade-off refers to a phenomenon where the intensity within the center of a large, flat cell body returns to a value nearly identical to the background, effectively "hollowing out" the cell’s representation in the digital image.8

Traditional segmentation methods, such as global thresholding, fail in this context because the intensity distributions of the cell interiors and the background overlap significantly. Furthermore, edge detection algorithms often struggle to differentiate between the true cell boundary and the artificial boundary created by the external edge of the halo.5 PHANTAST was specifically engineered to leverage these artifacts rather than merely filtering them, treating the halo as a signature of the cell's presence to refine the final segmentation mask.8

## **The PHANTAST Algorithmic Architecture**

The PHANTAST algorithm follows a multi-step pipeline designed for high sensitivity and high precision. It avoids the "black box" nature of many commercial tools by employing a transparent, rule-based approach that combines statistical texture analysis with directional gradient refinement.6

### **Primary Segmentation: Local Contrast Thresholding**

The first phase of the PHANTAST algorithm addresses the low contrast between the cytoplasm and the background. The algorithm does not operate on raw pixel intensities; instead, it evaluates the local pixel intensity homogeneity.5 In PCM, backgrounds are generally characterized by high homogeneity (low variance), while cellular regions—including the cell body and the associated halo—exhibit high local contrast and texture.8

The mathematical kernel of this step involves calculating the local variance or standard deviation within a defined neighborhood. For any given pixel ![][image1], the algorithm assesses the variability of intensities in a circular or square region determined by a scale parameter, ![][image2].11 If the local contrast exceeds a sensitivity threshold, ![][image3], the pixel is classified as a potential cell pixel.6 This step is highly effective at capturing the entire footprint of the cell, including the "shaded-off" interior, because even a flat cell body retains more textural information than the empty culture surface.5 However, this coarse detection inherently includes the halo, which can lead to an overestimation of the cell area by 10% to 30%.9

### **Refinement: Post-hoc Halo Correction**

The second, "post-hoc" stage of the algorithm is the correction of these halo artifacts.5 To resolve the true biological boundary, PHANTAST utilizes the direction of the intensity gradient. Because the halo represents a specific optical transition from the high-refractive-index cell to the background, the gradient of intensity across the halo follows a predictable pattern.8

The algorithm analyzes the vectors of intensity change at the perimeter of the coarse mask. By identifying where the gradient direction aligns with the characteristic signature of a PCM halo, the tool can prune away the bright glowing pixels that do not belong to the cell body.8 This allows the mask to "shrink" back to the actual contour of the cell, as confirmed by validation against ground-truth images where cell boundaries were manually traced or identified via fluorescence.5 The result is a precise segmentation that conforms to the physical boundary of the cell, even in complex morphologies like dendritic projections or flat cell bodies.8

| Segment | Logic | Objective |
| :---- | :---- | :---- |
| **Coarse Masking** | Local Contrast Thresholding ($ \\sigma, \\epsilon $) | Identify all cell-associated pixels 8 |
| **Artifact Pruning** | Gradient Direction Analysis | Remove halo pixels to find true boundary 5 |
| **Morphology Refining** | Area/Circularity Filtering | Exclude debris, bubbles, or non-cellular objects 12 |
| **Quantification** | Area Fraction Calculation | Output percentage confluency and cell density 6 |

## **Technical Parameters and Sensitivity Analysis**

The flexibility of PHANTAST across different cell types and microscopes is achieved through the adjustment of its primary hyperparameters: sigma (![][image2]) and epsilon (![][image3]). These parameters dictate the scale and sensitivity of the texture detection.11

### **Scale Parameter: Sigma (![][image2])**

Sigma defines the radius of the neighborhood used for the local contrast calculation. It is the most influential parameter regarding the scale of the objects to be detected.11

* **Low Sigma (1.0 to 2.0):** This setting is optimized for high-magnification images or cell types with intricate, fine-scale features, such as neuroblastoma (NB) cells with thin dendritic projections.11 While it captures high detail, it is more susceptible to sensor noise and small debris.12  
* **High Sigma (4.0 to 16.0):** This is the standard for lower magnification (4x or 10x) or for large, flat cells like Chinese Hamster Ovary (CHO) or human embryonic stem cells (hESC).8 Higher sigma values provide a smoothing effect that bridges gaps in the cytoplasm of large cells but may miss very fine appendages.11

### **Sensitivity Parameter: Epsilon (![][image3])**

Epsilon acts as the threshold for the local contrast filter. It determines the minimum variance required to differentiate a cell from the background.12

* **Lower Epsilon (0.03 to 0.05):** Increases the sensitivity of the tool, allowing it to detect cells with very low contrast or those in murky media. However, this may lead to false positives if the background has significant unevenness or artifacts.12  
* **Higher Epsilon (0.08 to 0.15):** Increases the specificity of the tool. It is often necessary in cultures with significant debris, precipitate, or uneven illumination where the "background" might otherwise trigger a detection.12

The interplay between these parameters is crucial. For instance, in images with degraded quality due to condensation or temperature fluctuations between the incubator and the microscope, a higher epsilon is typically combined with a moderate sigma to ensure that only the most distinct cellular features are recorded.8

## **Implementation and Accessibility in Research Environments**

PHANTAST was designed to be platform-agnostic, ensuring that researchers can use the tool regardless of their computational expertise. It is primarily implemented in MATLAB (96.2%) for its robust numerical processing capabilities, with performance-intensive segments written in C++ to achieve processing speeds of less than one second per megapixel image.6

### **The FIJI/ImageJ Ecosystem**

The most accessible version of PHANTAST for many biologists is the FIJI/ImageJ plugin.6 By integrating with the widely used FIJI distribution, PHANTAST leverages the "batteries-included" nature of the software, allowing users to combine PHANTAST segmentation with other ImageJ tools like "Particle Analysis" or "Coloc 2".17 The plugin features a graphical user interface (GUI) with a "preview" function, which is essential for determining the optimal ![][image2] and ![][image3] values before running large-scale batch analyses.11

### **MATLAB and Standalone Versions**

For developers and power users, the MATLAB toolbox provides the source code, enabling the integration of PHANTAST into custom high-throughput screening pipelines or microfluidic monitoring systems.6 A standalone GUI is also available for those who do not require the full ImageJ or MATLAB environments, providing a streamlined path from image upload to confluency data.6 This commitment to open-source transparency stands in contrast to commercial "black box" algorithms, allowing researchers to verify the logic and modify the code for specialized needs.6

## **Quantitative Outputs and Metric Definitions**

The primary output of PHANTAST is the confluency measurement, but the tool’s ability to generate precise masks allows for several advanced metrics vital for characterizing adherent cultures.5

### **Confluency: The Area Fraction (![][image4])**

Confluency is calculated as the Area Fraction (![][image4]), which is the ratio of pixels covered by cells to the total pixels in the growth area. Mathematically, it is expressed as:

![][image5]  
.2

This measurement is crucial for determining the timing of passaging or the initiation of differentiation protocols.1 For example, pluripotent stem cells are typically passaged at 70-80% confluency to prevent spontaneous differentiation caused by over-crowding.1

### **Cell Density and Morphology**

PHANTAST enables the estimation of cell density (cells per ![][image6]) even in colony-forming cell lines where individual cell boundaries are not visible.5 By analyzing the total segmented area and the typical morphological footprint of a single cell, the tool can provide a more accurate population estimate than simple manual counting.5 Furthermore, the high-fidelity masks allow for the measurement of:

* **Perimeter and Area:** Essential for tracking cell spreading or contraction.5  
* **Circularity:** A key metric for identifying morphological changes, such as the transition from elongated to cobblestone appearance in NIH 3T3 cells.3  
* **F-score and Jaccard Index:** Statistical measures used to validate the accuracy of the segmentation against a ground truth (![][image7]) and the segmented image (![][image8]):

![][image9]  
.20

## **Validation and Benchmarking Performance**

PHANTAST has been rigorously validated across a diverse range of cell lines and imaging conditions. Its performance is typically measured using the F-score, which balances precision (positive predictive value) and recall (sensitivity).8

### **Comparative Performance Metrics**

In head-to-head comparisons, PHANTAST consistently outperforms standard thresholding methods and rivals complex trainable segmenters while maintaining superior speed.7 Validation datasets including mESC, hESC, CHO, and NB cells showed high consistently high performance:

| Cell Line | Morphological Type | PHANTAST F-Score | Contextual Detail |
| :---- | :---- | :---- | :---- |
| **CHO** | Fibroblastic/Flat | ![][image10] | High contrast, robust detection 8 |
| **NB** | Dendritic/Small | ![][image11] | Intricate structures captured 8 |
| **mESC** | Colony-forming | ![][image12] | High density, complex boundaries 11 |
| **hESC** | Colony-forming | ![][image13] | Superior to Weka (![][image14]) 11 |

### **Comparison with Unsupervised Methods**

Research comparing PHANTAST to the Empirical Gradient Threshold (EGT) method found that PHANTAST's dedicated halo removal logic provided a 40% reduction in error compared to conventional active contour methods.7 While EGT relies on image histograms, PHANTAST's use of local contrast and directional gradients allows it to handle the "shade-off" problem more effectively, where the center of a cell would otherwise be misclassified as background.5

## **Industrial and Clinical Significance**

The standardization of confluency measurement is not merely a convenience but a requirement for the industrialization of cell-based therapies. In biomanufacturing, confluency is a critical "in-process control" (IPC).14

### **Process Consistency and Quality Control**

Manual estimation by eye can vary by as much as 10-20% between researchers.1 Such variability can have cascading effects:

* **Over-confluency:** Leads to nutrient depletion, pH shifts, and contact inhibition, which can permanently alter the gene expression or potency of the cells.1  
* **Under-confluency:** Results in sub-optimal seeding densities for subsequent steps, extending culture timelines and increasing production costs.1 PHANTAST provides a repeatable, objective metric that ensures every batch of cells is handled at the exact same physiological stage, regardless of the operator.14

### **Specialized Applications in Stem Cell Biology**

For induced pluripotent stem cells (iPSCs) and embryonic stem cells (ESCs), maintenance of the undifferentiated state is paramount. These cells grow in colonies, making confluency assessment more complex than for mesenchymal or epithelial monolayers.2 PHANTAST is specifically optimized for these "colony-forming" lines, allowing researchers to monitor the expansion of stem cell colonies non-invasively.5 This is vital for clinical applications where the use of chemical dyes for confluency estimation is prohibited due to their potential toxicity or interference with the final therapeutic product.1

## **Handling Image Degradation and Environmental Artifacts**

A major strength of PHANTAST is its robustness against common laboratory imaging issues. PCM images are rarely perfect; they are often marred by environmental factors that can confound automated analysis.14

### **Condensation and Uneven Illumination**

Condensation on the lid of a culture flask is a frequent issue caused by temperature differentials between the incubator and the imaging environment. This reduces the overall contrast of the image and introduces large-scale artifacts.8 PHANTAST’s local contrast approach is inherently more robust to these "low-frequency" intensity variations than global thresholding, as it only considers pixel neighborhoods rather than the entire image histogram.5

### **Debris, Bubbles, and Scratches**

In industrial bioprocessing, cultures may contain debris from media components or dead cells. PHANTAST includes secondary filtering steps—such as size and circularity constraints—to exclude these non-cellular objects from the confluency count.12 If a sample is particularly murky, increasing the epsilon (![][image3]) parameter allows the algorithm to ignore the low-level noise while still capturing the high-contrast signature of living cells.12

| Artifact | Impact on Image | PHANTAST Mitigation |
| :---- | :---- | :---- |
| **Shade-off** | Hollow cell centers | Local contrast/texture detection 8 |
| **Halo** | Bloated cell boundaries | Post-hoc gradient direction analysis 5 |
| **Condensation** | Reduced global contrast | Neighborhood-based variance filtering 5 |
| **Debris** | False positives | Post-segmentation size/circularity filters 12 |

## **Advanced Operational Modes: Default vs. High Confluency**

The tool includes a "High Confluency" method specifically developed for images where cells form a dense, continuous sheet.14 In such cases, the background (empty space) is scarce, and the traditional concept of an "object" boundary begins to fail.

### **The Default Method**

The default method is optimized for low-to-medium confluency (10-70%). It focuses on identifying discrete cellular objects against a clearly visible background.14 It provides high-fidelity boundaries (marked in red in the UI) that are essential for morphological analysis and cell counting.5

### **The High Confluency Method**

When a culture reaches 80-100% confluency, the "High Confluency" method employs a texture segmentation logic that classifies the entire image into "cell-containing" and "background" regions.14 This method is more robust for identifying the small, remaining gaps in a nearly complete monolayer, ensuring that confluency is not overestimated as 100% too early.14 Researchers are encouraged to "switch methods" in the GUI if the default red boundaries no longer align with the cell edges in dense areas.14

## **Future Directions and the Role of Unsupervised Learning**

As the field of bioimage analysis moves toward deep learning and artificial intelligence, the role of tools like PHANTAST remains central. While deep learning models (e.g., PHC-Net or Omnipose) can achieve high accuracy, they require massive, annotated datasets and significant computational power.13 PHANTAST, being an unsupervised and rule-based algorithm, provides several unique advantages:

* **No Training Required:** It can be used immediately on new cell lines without the need for manual labeling.6  
* **Computational Efficiency:** It runs on standard CPUs in less than a second, making it ideal for integration into the low-power embedded systems of smart microscopes or incubator-housed monitoring devices.5  
* **Interpretability:** Because it is based on physical principles (gradients and variance), the failure modes are predictable and the parameters (![][image15]) have biological meaning.6

Future developments likely involve hybrid approaches, where PHANTAST is used to automatically generate high-quality "silver standard" training data for neural networks, or where it serves as a robust initial segmentation layer for more complex active contour models.7 Its integration into microfabricated bioreactors further points toward a future of "set-and-forget" cell culture, where PHANTAST-based systems autonomously decide when to feed, passage, or harvest cells based on real-time confluency and morphological data.8

## **Synthesis and Recommendations for Professional Practice**

The adoption of PHANTAST into routine laboratory and industrial practice addresses the critical need for objective, reproducible data in adherent cell culture. By overcoming the optical artifacts inherent to phase contrast microscopy, PHANTAST transforms qualitative visual inspection into a quantitative analytical process.5

For professional researchers, the successful implementation of PHANTAST requires:

1. **Standardization of Imaging:** Consistent illumination, focus, and magnification (ideally 4x-10x) are essential for maximizing algorithmic accuracy.14  
2. **Parameter Tuning:** The selection of ![][image2] and ![][image3] should be performed systematically for each cell line using the "preview" function, with ![][image16] and ![][image17] serving as a robust starting point for most mammalian lines.15  
3. **Method Selection:** Utilizing the "High Confluency" mode for dense monolayers ensures precision at the end of the growth cycle.14

In conclusion, PHANTAST stands as a powerful testament to the value of domain-specific algorithm design. By embedding the physics of light-matter interaction into its logic, it provides a level of performance and accessibility that empowers researchers to generate uncompromisingly high-quality data from the most ubiquitous imaging modality in biology.4

#### **Works cited**

1. How to Measure Cell Confluency \- Thermo Fisher Scientific, accessed on February 9, 2026, [https://www.thermofisher.com/blog/life-in-the-lab/how-to-measure-cell-confluency/](https://www.thermofisher.com/blog/life-in-the-lab/how-to-measure-cell-confluency/)  
2. Cell Confluency: Why It Matters and 3 Easy Methods \- Bitesize Bio, accessed on February 9, 2026, [https://bitesizebio.com/63887/cell-confluency/](https://bitesizebio.com/63887/cell-confluency/)  
3. Variability in Cell Confluency: Comparison of Human and CellAssist® Assessments | Thrive Bioscience, accessed on February 9, 2026, [http://www.thrivebio.com/wp-content/uploads/2024/10/Cell-Confluence-Assessment.pdf](http://www.thrivebio.com/wp-content/uploads/2024/10/Cell-Confluence-Assessment.pdf)  
4. Software \- SZITA LAB MICROFLUIDICS, accessed on February 9, 2026, [http://szitalab.weebly.com/software.html](http://szitalab.weebly.com/software.html)  
5. Automated Method for the Rapid and Precise Estimation of Adherent Cell Culture Characteristics from Phase Contrast Microscopy Images \- PMC, accessed on February 9, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4260842/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4260842/)  
6. Repository for the FIJI/ImageJ implementation of the phase contrast microscopy segmentation toolbox (PHANTAST) \- GitHub, accessed on February 9, 2026, [https://github.com/nicjac/PHANTAST-FIJI](https://github.com/nicjac/PHANTAST-FIJI)  
7. A Novel Method for Effective Cell Segmentation and Tracking in Phase Contrast Microscopic Images, accessed on February 9, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8158140/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8158140/)  
8. Method for the segmentation of phase contrast microscopy (PCM) images.... | Download Scientific Diagram \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/figure/Method-for-the-segmentation-of-phase-contrast-microscopy-PCM-images-A-i-Cropped\_fig4\_256612032](https://www.researchgate.net/figure/Method-for-the-segmentation-of-phase-contrast-microscopy-PCM-images-A-i-Cropped_fig4_256612032)  
9. Automated Method for the Rapid and Precise Estimation of Adherent Cell Culture Characteristics from Phase Contrast Microscopy Images \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/publication/256612032\_Automated\_Method\_for\_the\_Rapid\_and\_Precise\_Estimation\_of\_Adherent\_Cell\_Culture\_Characteristics\_from\_Phase\_Contrast\_Microscopy\_Images](https://www.researchgate.net/publication/256612032_Automated_Method_for_the_Rapid_and_Precise_Estimation_of_Adherent_Cell_Culture_Characteristics_from_Phase_Contrast_Microscopy_Images)  
10. Artifact Halo Reduction in Phase Contrast Microscopy Using Apodization \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/publication/225866765\_Artifact\_Halo\_Reduction\_in\_Phase\_Contrast\_Microscopy\_Using\_Apodization](https://www.researchgate.net/publication/225866765_Artifact_Halo_Reduction_in_Phase_Contrast_Microscopy_Using_Apodization)  
11. Development of an image processing method for automated, non-invasive and scale-independent monitoring of adherent cell cultures, accessed on February 9, 2026, [https://discovery.ucl.ac.uk/1461036/1/Thesis\_NJ\_Final\_New.pdf](https://discovery.ucl.ac.uk/1461036/1/Thesis_NJ_Final_New.pdf)  
12. Characterization of heterogeneous primary human cartilage-derived cell population using non-invasive live-cell phase-contrast time-lapse imaging \- PMC \- NIH, accessed on February 9, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8053735/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8053735/)  
13. A benchmarked comparison of software packages for time-lapse image processing of monolayer bacterial population dynamics \- NIH, accessed on February 9, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11302142/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11302142/)  
14. Cell and Gene Therapy Catapult Cell Confluency Tool, accessed on February 9, 2026, [https://ct.catapult.org.uk/resources/confluency-tool](https://ct.catapult.org.uk/resources/confluency-tool)  
15. Immunological synapse formation between T regulatory cells and cancer-associated fibroblasts promotes tumour development \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/publication/381325819\_Immunological\_synapse\_formation\_between\_T\_regulatory\_cells\_and\_cancer-associated\_fibroblasts\_promotes\_tumour\_development](https://www.researchgate.net/publication/381325819_Immunological_synapse_formation_between_T_regulatory_cells_and_cancer-associated_fibroblasts_promotes_tumour_development)  
16. Has anybody an idea how to evaluate confluency? \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/post/Has-anybody-an-idea-how-to-evaluate-confluency](https://www.researchgate.net/post/Has-anybody-an-idea-how-to-evaluate-confluency)  
17. Fiji: ImageJ, with "Batteries Included", accessed on February 9, 2026, [https://fiji.sc/](https://fiji.sc/)  
18. Molecular mapping and functional validation of GLP-1R cholesterol binding sites in pancreatic beta cells | eLife, accessed on February 9, 2026, [https://elifesciences.org/articles/101011](https://elifesciences.org/articles/101011)  
19. How to Determine Cell Confluency with a Digital Microscope \- Leica Microsystems, accessed on February 9, 2026, [https://www.leica-microsystems.com/science-lab/life-science/how-to-determine-cell-confluency-with-a-digital-microscope/](https://www.leica-microsystems.com/science-lab/life-science/how-to-determine-cell-confluency-with-a-digital-microscope/)  
20. On Benchmarking Cell Nuclei Segmentation Algorithms for Fluorescence Microscopy \- SciTePress, accessed on February 9, 2026, [https://www.scitepress.org/Papers/2020/89679/89679.pdf](https://www.scitepress.org/Papers/2020/89679/89679.pdf)  
21. Benchmarking performance with sensitivity, specificity, precision and recall | EPI2ME Blog, accessed on February 9, 2026, [https://epi2me.nanoporetech.com/benchmarking-performance/](https://epi2me.nanoporetech.com/benchmarking-performance/)  
22. A Method for Quick, Low-Cost Automated Confluency Measurements \- ResearchGate, accessed on February 9, 2026, [https://www.researchgate.net/publication/51749941\_A\_Method\_for\_Quick\_Low-Cost\_Automated\_Confluency\_Measurements](https://www.researchgate.net/publication/51749941_A_Method_for_Quick_Low-Cost_Automated_Confluency_Measurements)  
23. PathoCellBench: A Comprehensive Benchmark for Cell Phenotyping \- MICCAI, accessed on February 9, 2026, [https://papers.miccai.org/miccai-2025/paper/4441\_paper.pdf](https://papers.miccai.org/miccai-2025/paper/4441_paper.pdf)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAZCAYAAACl8achAAACfUlEQVR4Xu2XzcuMURjGb0UR5bMQ4ZWUjY2viLwLQsrCSvkD7Ek2Fko2Niyod6FEiXyEkJIyZUFYWLCUIVEKGxTycf26nzNz5sw5Y95RRpqrfjVznzPnuZ5z3/c572s20ECj1lYxKQ3+RfHskTTYSZvEtTTYB00WK9NgTvPFI7EuHeiT8IKnoobES7EtHeij8IInvGW1U7wSc9OBPmqheGPurU1jxElxW0xMxtAscVw8E9fFYrFePBSPo3ndiAZjnT1iXBSnhveLpVEML3g6EcUaoltr4lQSR9TUDfPFeLmD4qO4KuaJC2JGY3Zn8Zw1Yrv4LFZEY+zmT7EliiE81Sxzms0WL8S+JI7Jw9bamLvFD7FZDIvvYkI03kn8hjWPiXdiSRUPmaYUKIlYh8wzMzOJF02PFausaYrvF0VdzDF/2LRqrBthkt/VzddhPUSmnlp+R/GENzy2qGQ6Ve6Bo9UO8zKIm2ut+Ga+q6n+2HRYnBLpVbky2GVechuiWFCxPEqNSEcTo9mYc8DcNOaD2LkgymijWBTFUtUqQhmEkktfJKjYiNTmGWs/8obNG+2W+SnyQHwSy6pxYperz4gMkPq6eSnlxEnEUTm1+s5p8qGKjw+TKoXNzB55iBSllwuf74tz4q55Hd4U98x34I41TwBEer+K99Z8sVTLxVvzda6YvyAvmitNdv61tWazRUOWv8a5AKinsAtkZXoFn3PCQMk064U1p5iX3BexOpoT9NtrHANHxVnr/WRA9AHN1tY45umOz+cF5k3G/Ph2DDpvfpmVNqchbitS14towCPmxnPC2BNxSTwXe618MZHJrv40DfoX/gk4nQYHGuh/1S+q03jtcO4wHQAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAYCAYAAADOMhxqAAAApElEQVR4XmNgGAWDEbACsS8QTwPiWUgYxNdDUgcGmkB8HYj/AvFzIP4PxO+A+BEQ3wBia4RSBgZ5IL4FxEuBmA8qdheIJ8FVIAEWIF7OADFdHEn8ABDvAWJuJDEwALn5HxC7oIl/BeIcNDEwAGkASRojiTEyQGyUQRKDA3UGiMc8kMRAtqHbiAKCgPgJEC8E4o1AfAhVGjsAxQHI0wLoEqOA5gAAKXobJEqiyYcAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAbCAYAAABBTc6+AAAAjElEQVR4XmNgGAVkAW4gDgXiaUA8BYjVYBKMQOwDxE+AeBIQOwCxOBCzwhT4AfFvII6BCSADfiA+AcRXgFgDiCWhmAOmQB+IPwHxDSCehYRNYQqMgfgrEJfDBNABzAScCjiBeDMQr2JAuBrkK1m4CiCQAOLtQHyQAWL/YSAuAGIWZEUgIMCA5v9RAAEA4eQTy4DyjIEAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAYCAYAAADtaU2/AAABi0lEQVR4Xu2UvStHURjHH6EUkpISUWIwyCAsmJQMP5NBWSxe/gNlkcGkrKSEQUpKkizSr4wWBlkMTCYpRUlevl/PPTnn6d7ftSjpfurTfXmec84953m6Ihl/jGLYBctt4DdpgFfwAw6ZmKMJjsAd0bz96Nk5Ca/hE+yMxhSkCC7Bd9EJc2E4oAweiuYNmxjhguewzgbi6IN7cEN0wpkgGlIPb+AdbA5DX3DBLVhpA5YqeAB7RBfkwrNBRsiA6MkcS9gL/dG1DS7DEi8WyzScFz3uKdGFN4OMkAXRHF4dpXDNu+dmCtICj2Bt9MzactJdif9iV1/ueFT0WFvhIrzw8lJZkbBB3DHmYYX33sGasrYvonVchSfwDa57ealsw0bRL6eD8Blewhovz8GP5Ilw19y9Yw6Oec+JsJ6sq4WL38JH2GFi7NJT+Ap7TezHsIPZyZZqeCbxPwB2670kn0YqbAZOPmED8r2ruJ/IePQ+qfES6RatHwc7Hf7fyJdHznH2PX2A7RyckZHxv/kEK9RUglAipDsAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACEAAAAZCAYAAAC/zUevAAAB/klEQVR4Xu2VP0hVURzHv5KCQWpqJJKQmiCGWCCKgkNtOhRI0KAg4eLgoBgViIOLi9giCuKgOFiDUIG6OCkukksNhQhuQoOIECSIWH2//M7pnXft8d50RXwf+HDf/d1zz5/f+d3zgCtGDq2kRZF4bOTRcTpEf9CXsEnFSivdoHW0mx6637HSQg/oI9pIf9KOsEHcKBP7tCr6IC5UGz24gHrwaAID7nc9rQ2eJXGddtEtukLvu/hDF1NxNdBC+pru0D3YABV02t1/oc+QWLGu/bQTNoEJpChMBb/TBVpK39GvsBm/p/foOmyQVdjE1PljOkeXkNjnF/QMVohCV93/caqPMvfsH3fpLl2GZUOo8Rqsw1e0mG7TI9rs2ghV+2fYxD1PYO/rmhG5sJX+pu1B/DbNh2XoDmywX3QsaCOewio+5A09pW2ReEo0iA6Pb/RW5FmIBtLqNGjIJH0Q3N+AbZuypuxlhA4Ndb6I1J+O4vOwI7c6iBfQTSQPptPxhI4GsbQoZUrdcCSugWvoNViGlCkVpLbI47MYMgqbhCaj4tPk0/5pqYE+v4+wT80zQqdcrIke43w9+C3y+K1QdpSlPmdG+M9TL8/ST/Q5LAuiF4nVhczAjuCQQdi2faBvkbywtCj9+szKYSsKUUclOF8z2pqbkZhQ7H/xLFmyXD7+Aid5V0OGu6bGAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAZCAYAAADuWXTMAAABIElEQVR4Xu3SvUoDQRSG4SNqIQZEDESRNKkFCwUbAxZegvcgNhYWCilCmhSx8AJsrEQEwVbEO7DVykYrKy0EK/Hn/fbsxNnNiJYW+eCBZXb+zsyYDTODHg4T9rGC0X7vUsZRwxY+cYk5rKGNV1xhNu8/kDGc4Q2rpX875pNqgsnSvyxV3Ob0HaJJT8wHd6L2QrSaVj3GSNSuesO2p6L2QjbNZ2+Z17uALp6wi4nvrsWEej9wbn7KN3hGM+qXTKperXSBO9TztmRCvVpdu1BUt+pXvUt5WzLhKlR3yDSu7ZfBP93vIl7wiEbUXsg87m3wftfND/DB/PQrODLvnz29d/Ptxk7N37HuVHerHe3hANsa+NfozS9jw7yM+PEM8//zBXXjPCpp7pFuAAAAAElFTkSuQmCC>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAZCAYAAADqrKTxAAAA/0lEQVR4XmNgGFaADYgZ0QVhQAKI5wLxIyB+DsStQKwPxLOBmBtJHRxoAvE1IM6H8jmBeBYQ/2OAaMYALgwQSV80cUkgPgbESmjiYFAOxP+BOAFNXAyIuxggtmKAaAaIpq9AXAXEzKjS2IEMEF9ngGgE4V9A3M+Aw/PIAOT+FiB+yoDQPAeIWZAV4QN5QPwXiB8yQAxDASBTQoGYB4v4GgYcmkB+WcyAqQkU+0uB+AQQ86PJgePnPBCLoInLAvEtIM5AEwcDUPCCIjWSATVtgQJgDwMWWziAeC0QFwHxEQaIjY0MEINAmrAGNzsQ6zFAbABFJijthTBgJqVRMHAAAGg2Kc4x9RiwAAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAUCAYAAAD1GtHpAAACcUlEQVR4Xu2XPWhUQRSFj4gQMSb4QyCdaLBRUGMrKQwKEmLhDwgqFhYBEQvFWItYmCqFVYiIgtjZxKCFxaKNqIWFokiaWCgiRhQFQUTP4b7xzd59u+66G3fBOfCRfXfmTXbO3pk7AyQlJSUlJS2Cesk9Mk2Wk93kPdkbdyrQEjJO3pHBLDZAXmRxtUvnyE/HJ7Ina29Uoz7QCTpEPpPt2bMmf5U8hBlcTbvID3LRxWXaR7I5en5CrpEr5Djpydr+Rh1nYheZJfOkP4pr4t/JjijmpcxVVqlvLE0yjuuv79OMxnyg3ZJxMvAxWRXFwxI8HcW8Sqht4g1YVrfaxFaO1RJtgS3lEumO4odhRvilGksZXMvEEmxMtV8gZ8lL8pQcJcuy/o3K/7+2S/vgV1SaGIzQPlZNMrjIRC03b+Jr2B66FFZ8XpEpVDdS8WFyoABluI8J9a823qKqGRM3war4ZeSVWNX9LspNVBUeytqDTsL6HHHxoP/GRGkf7LhyimyALdubKDexSGF8bQkqbo3IZ37btZ68JQ/IyigelmQ9X1jF6QyZgP0oOl/qXVVvaQS2hGMFE31Bq0f1fKd/Kk1AEyk64miSyrRaWoHKJaSKrnd1/pT0+TlZ+7tHZfFpRB1norSNLCDfn/rIMzKJfK+TWbrVxBkWtoL7yA/l+7NYfNuZIeui53BDeoPKDK1HHWmijDpIPsAq7iNyB+W3FfU5T74hz05l0G1yixwj12Fj+OvcTthV8BI5AfuB5sjWuJPTaliBUlX3fCmICfXXe23VGtgy24g8A/8kHVmUkaqOunMrY4ukuNrVT5XabwFJSUlN6RexlJduUbD9xQAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAUCAYAAAD1GtHpAAACYUlEQVR4Xu2XO2gVQRSGjxghYkR8oKQ1YqMgaid2omChhQ8QIlhqZRFBaxEbqxSCjSAKooVYKT6wuMRGtFWsUiRNEFFRFITg4/+cHXbuybp3r8HsLeaDD3bPzu7snJ3Hjlkmk8lkMv+BNfKZvC5XygPyvTycFqpgmTwv38ldRWyLfFvEuQ5H5ZzcU5yvknflUzlSxPrhkA8MAifkF7m7OKfxN+QLCwn+G/vlD3nZxS/IT3J7cc5zeF5MKlAXdVJ3vwxcEoflQzkjR5M4iZiXe5OYh577y0LZFBqZxn8mxxHqos57cshd68VpH2ib2JhXcm0Sp9EkYiKJeTpWn8TbFnofx+NdJcp6p+Umd60Xvr7W2WFhWHWse36i0TTeD9UUenBdEjsWnsmxH4J8MD4cc+Vmd60Xvr7WYW76ZguTGBNxM4l5SHBVEhluvZJIvGOh7jgXp6yQ++SxCunhPoaU574lZzFJ3GZhFb9q5aLB6v7YchL/0CSJcER+lmflmLwk79jik1iH7/mtw3zEvPRcrk7icUg2eWEWiXPyioWE8H/JvazewDHJTtkg39jCv4ImNHmnJSVO8L4xcXX2jffw4+yHECs698Z/wKqPEVdn//Ga4J81EOyUH+XJ4nyjfC0nrZzrSBa7mrSHxalgysqfcnYnxNLdzjX5Uq5PYmcs7HSYV/tlIJNIoo7LDxZWXBr8yLp3K5S5KL9b2TuZ1x7I+/KUvGXhGQeL65F18omF5/LrRB2Uq+vl3MMCNVvh14oYUp77WoWewgKw1bq3aHUst9AjWR3Zc9Njq2haLpPJ/BO/AR3Umu9i/m3yAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAUCAYAAAD1GtHpAAACgklEQVR4Xu2XS+jNQRTHj1DklUceWYiFkoVkRWw8Vyw8SpEtsaPYsrCwUxZKSpJSlJU8sviXjVgpj1IWJJJQQkrh+2lm/Oae+7u/e/9e97eYb32693d+587cOTNzzoxZUVFRUVHRP9A0cVucFRPFRvFWbMmdeuiQuCCmxmc+L4pbYnK0bROvxar4PElccj6j0WZvaIN2io9iRXweI86JuxYC3EsLLfgscvb54qlYH5/xoT3aTaIv+qTv0ap1QZwgronnYl5mPyK+idWZzYtAvBIrnX2KuGPVYL9baC8XfdHnFTHOveunvd4wbKXB3BfTMzuD/iEOZjavJeKdeCHWWrXS1ognFlYqop1d8XtS6veZmOPe9ZOfkKFrmYVtNWKd+YlBM/jjmc1rvDhjwQ/Oiw3isdia+fHOb0EmjIkjV/p00E+tCyJb8rN1B5FBp8A0iSJBvkuBZOsesM78VxdE+hqx0HfKxbmYoHView0ULm8D/Pndf9efBnGuuCmuWtjWKZinrRpQCWJm81pgIfcdtrDyON6csiqQ+6Lf7wSxSa3bzuQj8hLVlKqaRAVk8E1/+Kh1B59gbhIfLJw92e60k+dINEs8su5TwSBq+k9DUUrwfjCpOvvB5yJIvVYqBYkgEay6yUjV2U/eIPJttULLxXuxOz7PFg/FSasKBCuKoBEQbjaISszNhhtOLrb5A6tuPOTHe2LmL4+w1d+IpZltULUyiARqh4UzHyuIAV+3ztsKPsfEV6tWJ7b94ou4bOFYdEK8FHviezTDQvGhXXzog76aVjm/uWGhWHk+1dgAf343VLFSKACLrfOI0k8Em9VIheSz7qo41kIBST6s7KKior+mn53pmPI2wkU7AAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAUCAYAAAD1GtHpAAACYklEQVR4Xu2XT4hOURjGH6FGSEbRlNWQEuVfWWh2GmVhlD+lKEs7C4rsZpKNlYWFhZIp2Vn5t5C+zGZipZRSFmwkIaKUxPN0znHf73Xv7d7ku185T/1q7nvPmfud577vec8FsrKysrKy/oFWkAfkKllC9pB3ZMoOKtECcoa8JdtjbD15HuO6L10h58nSyDnygzwla+OYNtrnA8OgI+Qz2RGvtfhrZB7B4CpNIphxwcXPko9kc7x+TfajMHURwgv7SaZjrI2GzsQRcoe8ImMmLiO+kwkT80pGaKyVFmnj+vslWfN7BHAgxntkmYk30Qkf6FoyTgY+IStNXAZokadMzKuHehNvIGSftoa76DcrjfHPbSL/vM61BaGUe+hf5FGERfpStVIG15nYQ3WWpZd0E6G828g/r3NpH/yKPxecjLhuYl4yuMxElVudiavIY4R9c6e7l7SY7CaHSlCG+5jQeM0buP7GxE0IpXoZRdNQd7+PahNTR9d+e9Dds/pvTJTUID6Rk2QdwlFGJVploozT+MMojG8rn/mda5y8IXNkuYmnkmzyg9WcTpOLCC9F50vNVfe2Uum+ILtcvK2a/KaBSp1RHbLsiCMjlGl10uHZl5A6uubq/Jm0kTwkW01MRx5lun15TTR0JkrbyAdyLF6vJs/IJRQlJ7P0VWMzLG0Fj1AcylWuitmvnTSvjLruX6WhNFFGaY96j7Aodc576P9a0ZgZ8g1Fdmq/u01ukeNkFuF/7I33k7xxFh2lyjSK0KD0teP5UhITGq95nUpHDzWUDWi+6S9EyEh1R31zK2OzsrIGrl//SpvTLbt98gAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAYAAACaq43EAAABvElEQVR4Xu2UPyhGURjGX6EICSWKxWBRJIP8mWVh8KcUO7PFyqAMBoOyKDHKSFKGG4sYLCYsJoMYlFIKz+N97/3OPd+5GD6T76lf3z3v95z3nPve9xyRoor6Y9WCY7AJKsEQeACjrilD5WAV3IJOiw2De9Bn43Eb99u4yn5lCjyDHhuXgC1wJrqp7zQnOrfXxtUgAh9gxGLMw3zMm6gCHIA70OzEF8AbGHRivlrBjeh85ok1AJZAk43fRfOlxMW46AWoc+I0ctfzTszXtKhn2f/DEz30ptQlWqpItEyxfpOUPUHPCtgG++AanIAWx+eWPRG/64vkL0wjJzBhllhiep4k943ZbLvgCjRarOALR6KePVDmxMcsvmjjgi8cv7HfOPFcHlEeneDCbaJn7BTUOPFZCSd1xU2FPPHCkejL8JlVSImdzI4OHafgBEdZmwst7Hu+1C3aIDM2ZlOwOdYkd+hZMpaOSdjNFL8rn89Bg8XoXxe9+TostuF5EtE8CR5Fjw9Nh5K+tejhpfAq6SrwkuCGLkUrsCPp65KqB0eieXlM844od8QytYt3vf2gUtEmnRC955O72JHv+Wf6BMsWblrMODFBAAAAAElFTkSuQmCC>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAZCAYAAAAiwE4nAAABU0lEQVR4Xu2TvSuGURiHb2EQiYWEfKREsZCF0cBgkdGfYEEWFmW2SAZlMMjAYmEx+QOspCwSE5vRx/V7z/NwPwd5X3rL8Fx1Dec+5zlfz++Y5eTk/DeqcQq3cNup9qAbVyztuGhhjnVs8Z19eIHPeI+v+Ig3eImjH0N/pBY38AEXcASbsDId0IFXuIf1Sa3Twke/QSe6w564Q1ThvoXTNbt6HZ5a2G2pvOCmhSuUmle/q4CuUkdfTQsJjXhoYUOlot9xYtkMaJ0CCol2NJ4WEoZwLqoViw7wvkCMFnyysEBKBa5hm6t5BnDMXAgiFLruuJjSayGJE66m0ypEX9GFtxZuxX/jUbpnXbsGW13bpi1MsotHeIb9foBDYTq2sOBS1Jcyidd4gDt4jjOZERZSpDQ1xB3foFuYj4sOXbfeXub9/YUV+xy0sqBnsozDcUdOTll4A70HNV3SM5VIAAAAAElFTkSuQmCC>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAZCAYAAAChBHccAAABX0lEQVR4Xu2UPy8FQRTFj6CTkCj8iUSImkJEfACFFh2FUnwBpUojIqISjdAqlBrFRsMnUKiQh0SNTjgn12z2TfbtPIVnXjK/5JeXzM5sztx37wKJRCJmJukG7fIfxE4vvaIZ7al/FDfz9IK+og3Dn9M5+oCK8J10lu7QI88tNDj0x6i/l+gQKsIP0kv6Bft79PtJa/SRnqHkUIHlXzpqx4IouC7QMLxedAcbiJGftWNY8DG3KYAfLmQz4bVHLSNKw3fQffpMJ9wi2aTvdLqw1kq66SFsWEVp+HH6Aqu0LuLYxv+GX6QHdBgWfIo+0WtYkfu0aQHW3yt2JiejN7DvazP4bREy1DbrsFlz+nO4p00K/0Zn7EzOB1311qrww4UMhfdRB6gTMhTaRgOpm6y5BdjQ7sL6LhZUXBU0g/e1UfXv6Sk9obewb34sqOJqmaLKmaMqD9B+1A9uIpFIJNqXb4LpVblP4R1XAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAZCAYAAACIA4ibAAACjElEQVR4Xu2WTaiNURSGX6HI/09JkZtMlCJiREkkAxJGlJRiIgOSiZLBnRsokpKB8leSlIF0S0kUEVHSLSlJUoqB//e969vnrL2ur9MZ+O6h/dbTPXft/Z6zv/WttfcGioqKiv4/jSOLKrqR9+lzncaSpWRqHOg1jSI7yRtyhOwnh2AP0Enyet9L/Nm7hjwnp8ljcolMz2b0iPRGb5A7ZJKLXyH3yBQXi0pe7xuD4d4D5DwseUnLyRMy28V6QvPJW3KLTHDxc+QLbOF1Sl7vk6L3MPlI1rdmAJvIUzLTxVoaTZaRY+QomZgP/1WtJN9gD+F1hvwiG0PcK3mjonc1+VHF1CbzYG2ztRrPtBBWOo/IbjIDeWlF6cu2dYk8ddKitdCYEL1VxfW3TskbFb16nn2wpHwlg2RdFc+0AlZK6rnxYaxO/2JCpMmw31Bc3CV9bnxoQ7pKvpPNsM1FqH2aVBMJ0QtRi+wi28nnalynzpxqTmtDek/Owo4j0fSuu5b8xPCE9MMWvSXEvZI3yntV+dfJCbRbREm4Vs3ZW8WGNlFlKh5HnaRsx5bohDx10h72gQwg38yVIG2Y2jjrlLzxEPDeNCduzrNgFXIqBVKFjHRC9AZvkgdkmovrfvEM7WNRrawHXIz2epPX+9LdJHlVDbq4xUpTEgfgKkRfepy8Qr65NN0ykhb7iaxyMT3EQff/BliJ623rrSfJ630LkHt1UTtJbiO/mermeh9uD5F0oVFSXsPK7CJsYtPSNVtX70Gyh+yAlbI/+ZQEVbROB10NkuT1vocY7tWN9QJ5V825TF6QJW5OJpWZKsP/0EhIfa1e16nXjbxvbhhLUkf0wVpY+2fTp2lRUVFRUVGR6TdGfp8AWSjL+QAAAABJRU5ErkJggg==>