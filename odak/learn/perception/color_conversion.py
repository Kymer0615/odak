import math
import torch


def rgb_2_ycrcb(image):
    """
    Converts an image from RGB colourspace to YCrCb colourspace.

    Parameters
    ----------
    image   : torch.tensor
              Input image. Should be an RGB floating-point image with values in the range [0, 1]. Should be in NCHW format [3 x m x n] or [k x 3 x m x n].

    Returns
    -------

    ycrcb   : torch.tensor
              Image converted to YCrCb colourspace [k x 3 m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
       image = image.unsqueeze(0)
    ycrcb = torch.zeros(image.size()).to(image.device)
    ycrcb[:, 0, :, :] = 0.299 * image[:, 0, :, :] + 0.587 * \
        image[:, 1, :, :] + 0.114 * image[:, 2, :, :]
    ycrcb[:, 1, :, :] = 0.5 + 0.713 * (image[:, 0, :, :] - ycrcb[:, 0, :, :])
    ycrcb[:, 2, :, :] = 0.5 + 0.564 * (image[:, 2, :, :] - ycrcb[:, 0, :, :])
    return ycrcb


def ycrcb_2_rgb(image):
    """
    Converts an image from YCrCb colourspace to RGB colourspace.

    Parameters
    ----------
    image   : torch.tensor
              Input image. Should be a YCrCb floating-point image with values in the range [0, 1]. Should be in NCHW format [3 x m x n] or [k x 3 x m x n].

    Returns
    -------
    rgb     : torch.tensor
              Image converted to RGB colourspace [k x 3 m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
       image = image.unsqueeze(0)
    rgb = torch.zeros(image.size(), device=image.device)
    rgb[:, 0, :, :] = image[:, 0, :, :] + 1.403 * (image[:, 1, :, :] - 0.5)
    rgb[:, 1, :, :] = image[:, 0, :, :] - 0.714 * \
        (image[:, 1, :, :] - 0.5) - 0.344 * (image[:, 2, :, :] - 0.5)
    rgb[:, 2, :, :] = image[:, 0, :, :] + 1.773 * (image[:, 2, :, :] - 0.5)
    return rgb


def rgb_to_linear_rgb(image, threshold = 0.0031308):
    """
    Definition to convert RGB images to linear RGB color space. Mostly inspired from: https://kornia.readthedocs.io/en/latest/_modules/kornia/color/rgb.html

    Parameters
    ----------
    image           : torch.tensor
                      Input image in RGB color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.
    threshold       : float
                      Threshold used in calculations.

    Returns
    -------
    image_linear    : torch.tensor
                      Output image in linear RGB color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    image_linear = torch.where(image > 0.04045, torch.pow(((image + 0.055) / 1.055), 2.4), image / 12.92)
    return image_linear


def linear_rgb_to_rgb(image, threshold = 0.0031308):
    """
    Definition to convert linear RGB images to RGB color space. Mostly inspired from: https://kornia.readthedocs.io/en/latest/_modules/kornia/color/rgb.html

    Parameters
    ----------
    image           : torch.tensor
                      Input image in linear RGB color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.
    threshold       : float
                      Threshold used in calculations.

    Returns
    -------
    image_linear    : torch.tensor
                      Output image in RGB color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    image_linear =  torch.where(image > threshold, 1.055 * torch.pow(image.clamp(min=threshold), 1 / 2.4) - 0.055, 12.92 * image)
    return image_linear


def linear_rgb_to_xyz(image):
    """
    Definition to convert RGB space to CIE XYZ color space. Mostly inspired from : Rochester IT Color Conversion Algorithms (https://www.cs.rit.edu/~ncs/color/)

    Parameters
    ----------
    image           : torch.tensor
                      Input image in linear RGB color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.

    Returns
    -------
    image_xyz       : torch.tensor
                      Output image in XYZ (CIE 1931) color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    a11 = 0.412453
    a12 = 0.357580
    a13 = 0.180423
    a21 = 0.212671
    a22 = 0.715160
    a23 = 0.072169
    a31 = 0.019334
    a32 = 0.119193
    a33 = 0.950227
    M = torch.tensor([[a11, a12, a13], 
                      [a21, a22, a23],
                      [a31, a32, a33]])
    size = image.size()
    image = image.reshape(size[0], size[1], size[2]*size[3])  # NC(HW)
    image_xyz = torch.matmul(M, image)
    image_xyz = image_xyz.reshape(size[0], size[1], size[2], size[3])
    return image_xyz


def xyz_to_linear_rgb(image):
    """
    Definition to convert CIE XYZ space to linear RGB color space. Mostly inspired from : Rochester IT Color Conversion Algorithms (https://www.cs.rit.edu/~ncs/color/)

    Parameters
    ----------
    image            : torch.tensor
                       Input image in XYZ (CIE 1931) color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.

    Returns
    -------
    image_linear_rgb : torch.tensor
                       Output image in linear RGB  color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    a11 = 3.240479
    a12 = -1.537150
    a13 = -0.498535
    a21 = -0.969256 
    a22 = 1.875992 
    a23 = 0.041556
    a31 = 0.055648
    a32 = -0.204043
    a33 = 1.057311
    M = torch.tensor([[a11, a12, a13], 
                      [a21, a22, a23],
                      [a31, a32, a33]])
    size = image.size()
    image = image.reshape(size[0], size[1], size[2]*size[3])
    image_linear_rgb = torch.matmul(M, image)
    image_linear_rgb = image_linear_rgb.reshape(size[0], size[1], size[2], size[3])
    return image_linear_rgb

def rgb_to_hsv(image, eps: float = 1e-8):
    
    """
    Definition to convert RGB space to HSV color space. Mostly inspired from : https://kornia.readthedocs.io/en/latest/_modules/kornia/color/hsv.html

    Parameters
    ----------
    image           : torch.tensor
                      Input image in HSV color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.

    Returns
    -------
    image_hsv       : torch.tensor
                      Output image in  RGB  color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    max_rgb, argmax_rgb = image.max(-3)
    min_rgb, argmin_rgb = image.min(-3)
    deltac = max_rgb - min_rgb
    v = max_rgb
    s = deltac / (max_rgb + eps)
    deltac = torch.where(deltac == 0, torch.ones_like(deltac), deltac)
    rc, gc, bc = torch.unbind((max_rgb.unsqueeze(-3) - image), dim=-3)
    h1 = bc - gc
    h2 = (rc - bc) + 2.0 * deltac
    h3 = (gc - rc) + 4.0 * deltac
    h = torch.stack((h1, h2, h3), dim=-3) / deltac.unsqueeze(-3)
    h = torch.gather(h, dim=-3, index=argmax_rgb.unsqueeze(-3)).squeeze(-3)
    h = (h / 6.0) % 1.0
    h = 2.0 * math.pi * h 
    image_hsv = torch.stack((h, s, v), dim=-3)
    return image_hsv


def hsv_to_rgb(image):
    
    """
    Definition to convert HSV space to  RGB color space. Mostly inspired from : https://kornia.readthedocs.io/en/latest/_modules/kornia/color/hsv.html

    Parameters
    ----------
    image           : torch.tensor
                      Input image in HSV color space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.

    Returns
    -------
    image_rgb       : torch.tensor
                      Output image in  RGB  color space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    h = image[..., 0, :, :] / (2 * math.pi)
    s = image[..., 1, :, :]
    v = image[..., 2, :, :]
    hi = torch.floor(h * 6) % 6
    f = ((h * 6) % 6) - hi
    one = torch.tensor(1.0)
    p = v * (one - s)
    q = v * (one - f * s)
    t = v * (one - (one - f) * s)
    hi = hi.long()
    indices = torch.stack([hi, hi + 6, hi + 12], dim=-3)
    image_rgb = torch.stack((v, q, p, p, t, v, t, v, v, q, p, p, p, p, t, v, v, q), dim=-3)
    image_rgb = torch.gather(image_rgb, -3, indices)
    return image_rgb


def rgb_to_lms(image):
    """
    Internal function to calculate LMS cone response at particular light spectrum. LMS conversion tensor is hard coded for an standard LCD display backlight.

    Parameters
    ----------
    image            : torch.tensor
                       Image RGB data to be transformed to LMS space [k x 3 x m x n] or [3 x m x n]. Image(s) must be normalized between zero and one.


    Returns
    -------
    lms_image_tensor : float
                       Image LMS data transformed from RGB space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    a11 = 12.245
    a12 = 2.6253
    a13 = 4.7270e-08
    a21 = 37.442
    a22 = 38.719
    a23 = 0.080662
    a31 = 2.2498
    a32 = 3.1804
    a33 = 34.629
    M = torch.tensor([[a11, a21, a31], 
                      [a12, a22, a32],
                      [a13, a23, a33]])
    size = image.size()
    image = image.reshape(size[0], size[1], size[2]*size[3])
    image_lms = torch.matmul(M, image)
    image_lms = image_lms.reshape(size[0], size[1], size[2], size[3]) 
    
    return image_lms


def lms_to_rgb(image):
    """
    Internal function to convert LMS cone response to RGB space. LMS conversion tensor is hard coded for an standard LCD display backlight.

    Parameters
    ----------
    image               : torch.tensor
                          Image LMS data to be transformed to RGB space [k x 3 x m x n] or [3 x m x n].


    Returns
    -------
    image_rgb           : float
                          Image RGB data transformed from RGB space [k x 3 x m x n] or [1 x 3 x m x n].
    """
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    a11 = 12.245
    a12 = 2.6253
    a13 = 4.7270e-08
    a21 = 37.442
    a22 = 38.719
    a23 = 0.080662
    a31 = 2.2498
    a32 = 3.1804
    a33 = 34.629
    M = torch.tensor([[a11, a21, a31], 
                      [a12, a22, a32],
                      [a13, a23, a33]])
    size = image.size()
    image = image.reshape(size[0], size[1], size[2]*size[3])
    image_rgb = torch.matmul(M.inverse(), image)
    image_rgb = image_rgb.reshape(size[0], size[1], size[2], size[3])       
    return image_rgb


def lms_to_hvs_second_stage(image):
    '''
    This function turns LMS stage [L,M,S] values into HVS second stage [(M+S)-L, (L+S)-M, (L+M+S)/3]
    Equations are taken from Schmidt et al "Neurobiological hypothesis of color appearance and hue perception" 2014

    Parameters
    ----------
    image                             : torch.tensor
                                        Image data at LMS space [k x 3 x m x n] or [3 x m x n].

    Returns
    -------
    third_stage                       : torch.tensor
                                        Image data at second stage of HVS

    '''
    hvs_second_stage = torch.zeros(image.shape[0], 3, image.shape[2],image.shape[3])
    hvs_second_stage[:, 0, :, :] = (image[:, 1, :, :] +  image[:, 2, :, :]) - image[:, 0, :, :]
    hvs_second_stage[:, 1, :, :] = (image[:, 0, :, :] +  image[:, 2, :, :]) - image[:, 1, :, :]
    hvs_second_stage[:, 2, :, :] = torch.sum(image, dim=1) / 3.
    return hvs_second_stage

def srgb_to_lab(image):    
    """
    Definition to convert SRGB space to LAB color space. 

    Parameters
    ----------
    image           : torch.tensor
                      Input image in SRGB color space[3 x m x n]
    Returns
    -------
    image_lab       : torch.tensor
                      Output image in LAB color space [3 x m x n].
    """
    if image.shape[-1] == 3:
        input_color = image.permute(2, 0, 1)  # C(H*W)
    else:
        input_color = image
    # rgb ---> linear rgb
    limit = 0.04045        
    # linear rgb ---> xyz
    linrgb_color = torch.where(input_color > limit, torch.pow((input_color + 0.055) / 1.055, 2.4), input_color / 12.92)

    a11 = 10135552 / 24577794
    a12 = 8788810  / 24577794
    a13 = 4435075  / 24577794
    a21 = 2613072  / 12288897
    a22 = 8788810  / 12288897
    a23 = 887015   / 12288897
    a31 = 1425312  / 73733382
    a32 = 8788810  / 73733382
    a33 = 70074185 / 73733382

    A = torch.tensor([[a11, a12, a13],
                    [a21, a22, a23],
                    [a31, a32, a33]], dtype=torch.float32)

    linrgb_color = linrgb_color.permute(2, 0, 1) # C(H*W)
    xyz_color = torch.matmul(A, linrgb_color)
    xyz_color = xyz_color.permute(1, 2, 0)
    # xyz ---> lab
    inv_reference_illuminant = torch.tensor([[[1.052156925]], [[1.000000000]], [[0.918357670]]], dtype=torch.float32)
    input_color = xyz_color * inv_reference_illuminant
    delta = 6 / 29
    delta_square = delta * delta
    delta_cube = delta * delta_square
    factor = 1 / (3 * delta_square)

    input_color = torch.where(input_color > delta_cube, torch.pow(input_color, 1 / 3), (factor * input_color + 4 / 29))

    l = 116 * input_color[1:2, :, :] - 16
    a = 500 * (input_color[0:1,:, :] - input_color[1:2, :, :])
    b = 200 * (input_color[1:2, :, :] - input_color[2:3, :, :])

    image_lab = torch.cat((l, a, b), 0)
    return image_lab    

def lab_to_srgb(image):
    """
    Definition to convert LAB space to SRGB color space. 

    Parameters
    ----------
    image           : torch.tensor
                      Input image in LAB color space[3 x m x n]
    Returns
    -------
    image_srgb     : torch.tensor
                      Output image in SRGB color space [3 x m x n].
    """
    
    if image.shape[-1] == 3:
        input_color = image.permute(2, 0, 1)  # C(H*W)
    else:
        input_color = image
    # lab ---> xyz
    reference_illuminant = torch.tensor([[[0.950428545]], [[1.000000000]], [[1.088900371]]], dtype=torch.float32)
    y = (input_color[0:1, :, :] + 16) / 116
    a =  input_color[1:2, :, :] / 500
    b =  input_color[2:3, :, :] / 200
    x = y + a
    z = y - b
    xyz = torch.cat((x, y, z), 0)
    delta = 6 / 29
    factor = 3 * delta * delta
    xyz = torch.where(xyz > delta,  xyz ** 3, factor * (xyz - 4 / 29))
    xyz_color = xyz * reference_illuminant
    # xyz ---> linear rgb
    a11 = 3.241003275
    a12 = -1.537398934
    a13 = -0.498615861
    a21 = -0.969224334
    a22 = 1.875930071
    a23 = 0.041554224
    a31 = 0.055639423
    a32 = -0.204011202
    a33 = 1.057148933
    A = torch.tensor([[a11, a12, a13],
                  [a21, a22, a23],
                  [a31, a32, a33]], dtype=torch.float32)

    xyz_color = xyz_color.permute(2, 0, 1) # C(H*W)
    linear_rgb_color = torch.matmul(A, xyz_color)
    linear_rgb_color = linear_rgb_color.permute(1, 2, 0)
    # linear rgb ---> srgb
    limit = 0.0031308
    image_srgb = torch.where(linear_rgb_color > limit, 1.055 * (linear_rgb_color ** (1.0 / 2.4)) - 0.055, 12.92 * linear_rgb_color)
    return image_srgb

