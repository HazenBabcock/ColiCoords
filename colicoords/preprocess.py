import mahotas as mh
import numpy as np
from colicoords.cell import Cell, CellList


def data_to_cells(input_data, initial_pad=5, final_pad = 7, cell_frac=0.5, rotate='binary', verbose=True):
    assert 'binary' in input_data.dclasses
    assert input_data.ndim == 3

    vprint = print if verbose else lambda *a, **k: None
    cell_list = []
    i_fill = int(np.ceil(np.log10(len(input_data))))
    for i, data in enumerate(input_data):
        binary = data.binary_img
        if (binary > 0).mean() > cell_frac or binary.mean() == 0.:
            vprint('Image {} {}: Too many or no cells'.format(binary.name, i))
            continue

        # Iterate over all cells in the image
        l_fill = int(np.ceil(np.log10(len(np.unique(binary)))))
        for l in np.unique(binary)[1:]:
            selected_binary = (binary == l).astype('int')
            min1, max1, min2, max2 = mh.bbox(selected_binary)
            min1p, max1p, min2p, max2p = min1 - initial_pad, max1 + initial_pad, min2 - initial_pad, max2 + initial_pad

            try:
                assert min1p > 0 and min2p > 0 and max1p < data.shape[0] and max2p < data.shape[1]
            except AssertionError:
                vprint('Cell {} on image {} {}: on the edge of the image'.format(l, binary.name, i))
                continue
            try:
                assert len(np.unique(binary[min1p:max1p, min2p:max2p])) == 2
            except AssertionError:
                vprint('Cell {} on image {} {}: multiple cells per selection'.format(l, data.binary_img.name, i))
                continue

            output_data = data[min1p:max1p, min2p:max2p].copy()
            output_data.binary_img //= output_data.binary_img.max()

            # Calculate rotation angle and rotate selections
            theta = output_data.data_dict[rotate].orientation if rotate else 0
            rotated_data = output_data.rotate(theta)

            if final_pad:
                min1, max1, min2, max2 = mh.bbox(rotated_data.binary_img)
                min1p, max1p, min2p, max2p = min1 - final_pad, max1 + final_pad, min2 - final_pad, max2 + final_pad

                min1f = np.max((min1p, 0))
                max1f = np.min((max1p, rotated_data.shape[0]))

                min2f = np.max((min2p, 0))
                max2f = np.min((max2p, rotated_data.shape[1]))
                #todo acutal padding instead of crop?

                final_data = rotated_data[min1f:max1f, min2f:max2f].copy()
            else:
                final_data = rotated_data
            #Make cell object and add all the data
            #todo change cell initation and data adding interface
            c = Cell(final_data)

            c.name = 'img{}c{}'.format(str(i).zfill(i_fill), str(l).zfill(l_fill))
            cell_list.append(c)

    return CellList(cell_list)