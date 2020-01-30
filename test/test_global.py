# TODO:
# 0. Clean up your code by doing:
#
# 1. Write unit tests for the following methods:
#
# 2. Write integration tests for the following:

import sys
sys.path.append('core');
from matplotlib import pyplot as plt

from matrices import *
from fresnel import *
from convolution import generateConvolutionMatrix

statuses = [];
messages = [];

def assertAlmostEqual(a, b, absoluteTolerance=1e-10, relativeTolerance=1e-9, errorMessage=""):
    np.testing.assert_allclose(a, b, atol=absoluteTolerance, rtol=relativeTolerance, err_msg=errorMessage);

def assertEqual(a, b, errorMessage=""):
    np.testing.assert_equal(a, b, err_msg=errorMessage)

def complexNumberArrayFromString(stringRow):
    delimiter = 'i'
    rowOfStrings = stringRow.split(delimiter)
    rowOfStrings = [elem + "j" for elem in rowOfStrings]
    rowOfStrings.remove("j")
    rowOfStrings = np.array(rowOfStrings)
    rowOfComplexNumbers = rowOfStrings.astype(np.cdouble)

    return rowOfComplexNumbers

def numpyArrayFromFile(filename):
    """ Requires input file with all columns together on the same 18 rows """
    fileHandle = open(filename, 'r')
    delimiter = 'i'
    fileLines = fileHandle.readlines()
    data = None
    i = 0
    for line in fileLines:
        line = line.replace(" ", "")
        if line is not "":
            rowOfStrings = line.split(delimiter)
            rowOfStrings = [elem + "j" for elem in rowOfStrings]
            rowOfStrings.remove("\nj")
            rowOfStrings = np.array(rowOfStrings)
            rowOfComplexNumbers = rowOfStrings.astype(np.cdouble)
            if i is 0:
                data = rowOfComplexNumbers
            else:
                data = np.vstack((data, rowOfComplexNumbers))
            i += 1

    return data;

def numpyArrayFromSeparatedColumnsFile(filename):
    """ Requires an input file with columns 1 through 6 in the first 18 columns followed by a
    vertical spacer followed by columns 7 through 12 and so on """
    fileHandle = open(filename, 'r')
    fileLines = fileHandle.readlines()
    data = [None, None, None]
    rowNumber = 0
    columnNumber = 0

    for line in fileLines:
        line = line.replace(" ", "")
        line = line.replace("\n", "")
        if line is not "":
            rowOfComplexNumbers = complexNumberArrayFromString(line)

            if rowNumber is 0:
                data[columnNumber] = rowOfComplexNumbers
            else:
                data[columnNumber] = np.vstack((data[columnNumber], rowOfComplexNumbers))
            rowNumber += 1

        if line is "": # This indicates we should start a new set of columns and append it to the old one
            columnNumber += 1
            rowNumber = 0

    data = np.hstack((data[0], data[1], data[2]))
    return data

class Test:
    def __init__(self):
        self.messages = []; # Messages sent back from our tests (strings)
        self.statuses = []; # statuses sent back from our tests (boolean)
        self.unitTestsEnabled = True;
        self.integrationTestsEnabled = True;

    def printResults(self):
        for s, i in zip(self.statuses, range(len(self.statuses))):
            if(s == False):
                print(self.messages[i]);
        print(f"{self.statuses.count(True)} PASSED, {self.statuses.count(False)} FAILED");

    def testCaller(self, testFunction, *args):
        test_status = False; # By default assume we failed the test.
        test_message = f"{testFunction.__name__}({args}): ";

        try:
            print(f"Calling function {testFunction.__name__} ... ", end=" ");
            testFunction(*args);
            print("OK");
            test_status = True;
            self.statuses.append(test_status);
            self.messages.append(test_message);
        except AssertionError as ae:
            print("FAIL");
            test_message += "FAILED";
            test_message += str(ae);
            self.statuses.append(test_status);
            self.messages.append(test_message);

    def runUnitTests(self):
        print("--------- RUNNING UNIT TESTS... ----------");
        self.testCaller(self.testSetupData1x1Harmonics)
        self.testCaller(self.testGenerateConvolutionMatrix)
        self.testCaller(self.testCalculateKz);
        self.testCaller(self.testTransparentSMatrix)
        self.testCaller(self.testCalculateKVector);
        self.testCaller(self.testCalcEz);
        self.testCaller(self.testaTEM);
        self.testCaller(self.testPMatrix);
        self.testCaller(self.testQMatrix);
        self.testCaller(self.testOMatrix);
        self.testCaller(self.testVMatrix);
        self.testCaller(self.testXMatrix);
        self.testCaller(self.testAMatrix);
        self.testCaller(self.testBMatrix);
        self.testCaller(self.testDiMatrix);
        self.testCaller(self.testS11i);
        self.testCaller(self.testS12i);
        self.testCaller(self.testS21i);
        self.testCaller(self.testS22i);
        self.testCaller(self.testDRed);
        self.testCaller(self.testFRed);
        self.testCaller(self.testRedhefferProductS11);
        self.testCaller(self.testRedhefferProductS12);
        self.testCaller(self.testRedhefferProductS21);
        self.testCaller(self.testRedhefferProductS22);
        self.testCaller(self.testSrefFull);
        self.testCaller(self.testStrnFull);
        self.testCaller(self.testCalculateInternalSMatrix);
        self.testCaller(self.testCalculatedReflectionRegionSMatrix);
        self.testCaller(self.testCalculatedTransmissionRegionSMatrix);
        self.testCaller(self.testCalculateRT);
        self.testCaller(self.setupData3x3HarmonicsOblique); # REMOVE THIS LINE ONCE YOU WRITE TESTS.
        print("--------- END UNIT TESTS... ----------");

    def runIntegrationTests(self):
        """
        Runs integration tests to verify s-parameters for composite code, to verify the output field
        for a given input field, and to verify the reflectance/transmittance and enforce power 
        conservation.
        """

        print("--------- RUNNING INTEGRATION TESTS... ----------");
        self.testCaller(self.itestGlobalScatteringMatrix);

        print("--------- END INTEGRATION TESTS... ----------");

    def testSetupData1x1Harmonics(self):
        self.setupData1x1Harmonics()
        absoluteTolerance = 1e-4
        relativeTolerance = 1e-3
        lambda0Actual = 0.02
        thetaActual = 0
        phiActual = 0

        pTEActual = 1
        pTMActual = 0

        urReflectionRegionActual = 1.0
        erReflectionRegionActual = 2.0
        urTransmissionRegionActual = 1.0
        erTransmissionRegionActual = 9.0
        urDeviceRegionActual = 1.0
        erDeviceRegionActual = 6.0

        xPeriodActual = 0.0175
        yPeriodActual = 0.015
        layer1ThicknessActual = 0.005
        layer2ThicknessActual = 0.003
        triangleWidthActual = 0.012

        NxActual = 512
        NyActual = 439
        xHarmonicsActual = 1
        yHarmonicsActual = 1
        dxActual = 3.418e-5
        dyActual = 3.4169e-5

        assertEqual(lambda0Actual, self.lambda0, "Free space wavelength not equal")
        assertEqual(thetaActual, self.theta, "Angle theta not equal")
        assertEqual(phiActual, self.phi, "Angle phi not equal")
        assertEqual(pTEActual, self.pTE, "TE polarization amount not equal")
        assertEqual(pTMActual, self.pTM, "TM polarization amount not equal")
        assertEqual(urReflectionRegionActual, self.urReflectionRegion, "ur in reflection region not equal")
        assertEqual(erReflectionRegionActual, self.erReflectionRegion, "er in reflection region not equal")
        assertEqual(erTransmissionRegionActual, self.erTransmissionRegion,
                "er in transmission region not equal")
        assertEqual(urTransmissionRegionActual, self.urTransmissionRegion,
                "ur in transmission region not equal")
        assertEqual(erDeviceRegionActual, self.erDeviceRegion, "er in device region not equal")
        assertEqual(urDeviceRegionActual, self.urDeviceRegion, "ur in device region not equal")
        assertAlmostEqual(NxActual, self.Nx, absoluteTolerance, relativeTolerance,
                "Nx not equal")
        assertAlmostEqual(NyActual, self.Ny, absoluteTolerance, relativeTolerance,
                "Ny not equal")
        assertAlmostEqual(xHarmonicsActual, self.numberHarmonics[0],
                errorMessage="number x harmonics not equal")
        assertEqual(yHarmonicsActual, self.numberHarmonics[1],
                errorMessage="number y harmonics not equal")
        assertAlmostEqual(xPeriodActual, self.xPeriod, absoluteTolerance, relativeTolerance,
                "x Period not equal")
        assertAlmostEqual(yPeriodActual, self.yPeriod, absoluteTolerance, relativeTolerance,
                "y Period not equal")
        assertAlmostEqual(layer1ThicknessActual, self.layerThickness[0], absoluteTolerance, relativeTolerance,
                "Layer 1 thicknesses not equal")
        assertAlmostEqual(layer2ThicknessActual, self.layerThickness[1], absoluteTolerance, relativeTolerance,
                "Layer 2 thickness not equal")
        assertAlmostEqual(dxActual, self.dx, absoluteTolerance, relativeTolerance,
                "dx not equal")
        assertAlmostEqual(dyActual, self.dy, absoluteTolerance, relativeTolerance,
                "dy not equal")

    def testGenerateConvolutionMatrix(self):
        absoluteTolerance = 1e-4
        relativeTolerance = 1e-3

        self.setupData1x1Harmonics()
        convolutionMatrixCalculated = generateConvolutionMatrix(self.urData[0], self.numberHarmonics)
        convolutionMatrixActual = 1
        assertAlmostEqual(convolutionMatrixActual, convolutionMatrixCalculated, absoluteTolerance,
                relativeTolerance, "UR convolution matrices for layer 1 not equal")


        convolutionMatrixCalculated = generateConvolutionMatrix(self.erData[0], self.numberHarmonics)
        convolutionMatrixActual = 5.0449
        assertAlmostEqual(convolutionMatrixActual, convolutionMatrixCalculated, absoluteTolerance,
                relativeTolerance, "ER convolution matrices for layer 1 not equal")

        convolutionMatrixActual = 1
        convolutionMatrixCalculated = generateConvolutionMatrix(self.urData[1], self.numberHarmonics)
        assertAlmostEqual(convolutionMatrixActual, convolutionMatrixCalculated, absoluteTolerance,
                relativeTolerance, "UR convolution matrices for layer 2 not equal")

        convolutionMatrixActual = 6
        convolutionMatrixCalculated = generateConvolutionMatrix(self.erData[1], self.numberHarmonics)
        assertAlmostEqual(convolutionMatrixActual, convolutionMatrixCalculated, absoluteTolerance,
                relativeTolerance, "ER convolution matrices for layer 2 not equal")


    def testCalculateKz(self):
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kx = 0
        ky = 0

        # First, we have some data for reflection region
        er = 2.0
        ur = 1.0
        kzActual = -1.4142
        kzCalculated = calculateKzReflected(kx, ky, er, ur)
        assertAlmostEqual(kzActual, kzCalculated, absoluteTolerance, relativeTolerance,
                "kz in reflection region not correct");

        # Now, we have some data for transmission region
        er = 9.0
        ur = 1.0
        kzActual = 3
        kzCalculated = calculateKz(kx, ky, er, ur)
        assertAlmostEqual(kzActual, kzCalculated, absoluteTolerance, relativeTolerance,
                "kz in transmission region not correct");

    def testTransparentSMatrix(self):
        """
        Tests the transparent S matrix function. Should generate a matrix with identities along the diagonal
        """
        absoluteTolerance = 1e-10;
        relativeTolerance = 1e-10;
        SActual = complexZeros((2,2,2,2));
        SActual[1,0] = complexIdentity(2);
        SActual[0,1] = complexIdentity(2);

        SCalculated = generateTransparentSMatrix();

        assertAlmostEqual(SActual, SCalculated, absoluteTolerance, relativeTolerance);


    def testCalculateKVector(self):
        """ Tests that the k-vector that our calculateKVector function is returning is correct
        """
        er = 1.4;
        ur = 1.2;
        absoluteTolerance = 0.00001;
        relativeTolerance = 0.0001;

        theta = 0;
        phi = 0;
        kVectorCalculated = calculateKVector(theta, phi, er, ur);
        kVectorActual = complexArray([0, 0, 1.29615]);
        assertAlmostEqual(kVectorActual, kVectorCalculated, absoluteTolerance, relativeTolerance);

        theta = 57;
        phi = 23;
        (kx_actual, ky_actual, kz_actual) = complexArray([1.00063, 0.424741, 0.705933])
        assertAlmostEqual(kVectorActual, kVectorCalculated, absoluteTolerance, relativeTolerance);

    def testCalcEz(self):
        kx = 1.0006;
        ky = 0.4247;
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;

        # For the incident layer (reflected electric field from Rumpf data):
        kz = 0.705933
        Ex = 0.0519 - 0.2856j;
        Ey = -0.4324 + 0.0780j;
        Ez_actual = 0.1866 + 0.3580j;
        Ez_calc = calculateEz(kx, ky, kz, Ex, Ey);

        assertAlmostEqual(Ez_actual, Ez_calc, absoluteTolerance, relativeTolerance);

        # For the transmitted layer (transmitted field from Rumpf data)
        kz = 1.3032;
        Ex = -0.0101 + 0.3577j;
        Ey = 0.4358 - 0.0820j;
        Ez_actual = -0.1343 - 0.2480j;
        Ez_calc = calculateEz(kx, ky, kz, Ex, Ey);
        assertAlmostEqual(Ez_actual, Ez_calc, absoluteTolerance, relativeTolerance);

    def testCalcRT(self):
        """
        Calculates reflectance and transmittance given the known fields at the output and
        the input of the device.
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kz_ref = 0.705933;
        kz_trn = 1.3032;
        ur_ref = 1.2;
        ur_trn = 1.6;
        Ex_ref = 0.0519 - 0.2856j;
        Ey_ref = -0.4324 + 0.0780j;
        Ez_ref = 0.1866 + 0.3580j;
        Exyz_ref = complexArray([Ex_ref, Ey_ref, Ez_ref]);

        Ex_trn = -0.0101 + 0.3577j;
        Ey_trn = 0.4358 - 0.0820j;
        Ez_trn = -0.1343 - 0.2480j;
        Exyz_trn = complexArray([Ex_trn, Ey_trn, Ez_trn]);
        R_actual = 0.4403;
        T_actual = 0.5597;

        (R_calc, T_calc) = calcRT(kz_ref, kz_trn, ur_ref, ur_trn, Exyz_ref, Exyz_trn);
        assertAlmostEqual(R_actual, R_calc, absoluteTolerance, relativeTolerance);
        assertAlmostEqual(T_actual, T_calc, absoluteTolerance, relativeTolerance);

    def testaTEM(self):
        """
        Tests the function that generates our normalized TE/TM vectors via cross products, and
        checks that they are properly normalized. I'm not actually sure if these vectors should
        be complex, because they should only be specifying a direction, but I am going to assume
        for now that they are.
        """
        absoluteTolerance = 0.00001;
        relativeTolerance = 0.0001;
        kx = 1.20318;
        ky = 0.694658;
        kz = 1.43868; # corresponds to an angle of 44deg, 30deg with nref = 2.
        # We only want the x and y components of our TE/TM vectors, as everything we do
        # discards the z-information until the very end
        aTE_actual = complexArray([-0.5, 0.866025, 0])[0:2];
        aTM_actual = complexArray([0.622967, 0.35967, -0.694658])[0:2];
        (aTE_calc, aTM_calc) = aTEMGen(kx, ky, kz);
        assertAlmostEqual(aTE_actual, aTE_calc, absoluteTolerance, relativeTolerance);
        assertAlmostEqual(aTM_actual, aTM_calc, absoluteTolerance, relativeTolerance);

        # Now, we also want to make sure to test the case where kx = ky = 0, as this
        # could make everything blow up.
        kx = 0;
        ky = 0.0001;
        kz = 1.5;
        aTE_actual = complexArray([0,1,0])[0:2];
        aTM_actual = complexArray([1,0,0])[0:2];
        (aTE_calc, aTM_calc) = aTEMGen(kx, ky, kz);
        assertAlmostEqual(aTE_actual, aTE_calc, absoluteTolerance, relativeTolerance);
        assertAlmostEqual(aTM_actual, aTM_calc, absoluteTolerance, relativeTolerance);

    def testPMatrix(self):
        """
        Tests the P - matrix (the matrix that relates the E field to the H-field) with self-generated data.
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kx = 0.601592;
        ky = 0.347329
        er = 1.0;
        ur = 3.0;
        P_actual = complexArray([
            [0.20895, 2.63809],
            [-2.87936, -0.20895]]);
        P_calc = calculatePMatrix(kx, ky, er, ur);
        assertAlmostEqual(P_actual, P_calc, absoluteTolerance, relativeTolerance);
        er = 2.5;
        ur = 1.1;
        P_actual = complexArray([
            [0.0835802, 0.955235],
            [-1.05174, -0.0835802]]);
        P_calc = calculatePMatrix(kx, ky, er, ur);
        assertAlmostEqual(P_actual, P_calc, absoluteTolerance, relativeTolerance);

    def testQMatrix(self):
        """
        Tests our Q matrix (the matrix we get from the differential equation in terms of Hx and Hy).
        Uses data available on Raymond Rumpf's website on computational electromagnetics.
        """
        # The data we have available is only accurate to the 4th decimal place. This should
        # be sufficient. kx and ky are given in the setup, fixed by our angles theta and phi.
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kx = 1.0006;
        ky = 0.4247;

        # Zeroth, we actually have data for our gap layer
        er = 1.0 + sq(kx) + sq(ky);
        ur = 1.0;
        Q_actual = complexArray([[0.4250, 1.1804],[-2.0013, -0.4250]]);
        Q_calc = calculateQMatrix(kx, ky, er, ur);
        assertAlmostEqual(Q_actual, Q_calc, absoluteTolerance, relativeTolerance);

        # First, we have some data for layer 1
        er = 2.0;
        ur = 1.0;
        Q_actual = complexArray([[0.4250, 0.9987],[-1.8196, -0.4250]]);
        Q_calc = calculateQMatrix(kx, ky, er, ur);
        assertAlmostEqual(Q_actual, Q_calc, absoluteTolerance, relativeTolerance);

        # Now, we have some data for layer 2.
        er = 1.0;
        ur = 3.0;

        Q_actual = complexArray([[0.1417, 0.6662],[-0.9399, -0.1417]]);
        Q_calc = calculateQMatrix(kx, ky, er, ur);
        assertAlmostEqual(Q_actual, Q_calc, absoluteTolerance, relativeTolerance);

    def testOMatrix(self):
        """
        Tests the omega matrix (aka the lambda matrix).
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kx = 1.0006;
        ky = 0.4247;

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;

        O_actual = complexArray([[0 + 0.9046j, 0+0j],[0+0j,0+0.9046j]]);
        O_calc = calculateOmegaMatrix(kz);
        assertAlmostEqual(O_actual, O_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;

        O_actual = complexArray([[0 + 1.3485j, 0+0j],[0+0j,0+1.3485j]]);
        O_calc = calculateOmegaMatrix(kz);
        assertAlmostEqual(O_actual, O_calc, absoluteTolerance, relativeTolerance);

    def testVMatrix(self):
        """
        Tests the V matrix (the matrix that relates the magnetic field and the electric field modes)
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        kx = 1.0006;
        ky = 0.4247;

        # GAP DATA
        er = 1.0 + sq(kx) + sq(ky); # Apparently this is a convenient gap choice.
        ur = 1.0;
        kz = 1.0; # er being the above value makes this true

        (V_calc, W) = calculateVWXMatrices(kx, ky, kz, er, ur);
        V_actual = complexArray([[0 - 0.4250j, 0 - 1.1804j], [0 + 2.0013j, 0 + 0.4250j]]);
        assertAlmostEqual(V_actual, V_calc, absoluteTolerance, relativeTolerance);

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;

        (V_calc, W) = calculateVWXMatrices(kx, ky, kz, er, ur);
        V_actual = complexArray([[0-0.4698j,0-1.1040j],[0+2.0114j,0+0.4698j]]);
        assertAlmostEqual(V_actual, V_calc, absoluteTolerance, relativeTolerance);


        # LAYER 2 DATA
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;

        (V_calc, W) = calculateVWXMatrices(kx, ky, kz, er, ur);
        V_actual = complexArray([[0-0.1051j,0-0.4941j],[0+0.6970j,0+0.1051j]]);
        assertAlmostEqual(V_actual, V_calc, absoluteTolerance, relativeTolerance);

        # REFERENCE REGION DATA
        er = 1.4;
        ur = 1.2;
        kz = 0.705995; # Calculated manually using er and ur above.
        (V_calc, W_ref) = calculateVWXMatrices(kx, ky, kz, er, ur);
        V_actual = complexArray([
            [0 - 0.5017j, 0 - 0.8012j],
            [0 + 1.7702j, 0 + 0.5017j]]);
        assertAlmostEqual(V_actual, V_calc, absoluteTolerance, relativeTolerance);

    def testXMatrix(self):
        """
        Tests the X matrix (the matrix exponential of the omega matrix)
        """
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)
        kx = 1.0006;    # x component of k vector
        ky = 0.4247;    # y component of k vector
        l0 = 2.7;       # Free-space wavelength
        k0 = 2.3271;    # Free-space wavenumber

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;
        L = 0.25*l0;

        (V, W, X_calc) = calculateVWXMatrices(kx, ky, kz, er, ur, k0, L);
        X_actual = complexArray([[0.1493+0.9888j, 0+0j],[0+0j,0.1493+0.9888j]]);
        assertAlmostEqual(X_actual, X_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;
        L = 0.5*l0;

        (V, W, X_calc) = calculateVWXMatrices(kx, ky, kz, er, ur, k0, L);
        X_actual = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);
        assertAlmostEqual(X_actual, X_calc, absoluteTolerance, relativeTolerance);

    def testAMatrix(self):
        """
        Tests the A matrix (an intermediate matrix in calculating the scattering parameters of a given layer)
        """
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)
        kx = 1.0006;    # x component of k vector
        ky = 0.4247;    # y component of k vector
        l0 = 2.7;       # Free-space wavelength
        k0 = 2.3271;    # Free-space wavenumber

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;
        L = 0.25*l0;
        W1 = np.identity(2);
        Wg = np.identity(2);
        V1 = complexArray([[0 - 0.4698j, 0 - 1.1040j],[0 + 2.0114j, 0 + 0.4698j]]);
        Vg = complexArray([[0 - 0.4250j, 0 - 1.1804j], [0 + 2.0013j, 0 + 0.4250j]]);

        A_calc = calculateScatteringAMatrix(W1, Wg, V1, Vg);
        A_actual = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        assertAlmostEqual(A_actual, A_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;
        L = 0.5*l0;

        W2 = complexIdentity(2);
        Wg = complexIdentity(2);
        V2 = complexArray([[0 - 0.1051j, 0 - 0.4941j],[0 + 0.6970j, 0 + 0.1051j]]);
        Vg = complexArray([[0 - 0.4250j, 0 - 1.1804j],[0 + 2.0013j, 0 + 0.4250j]]);

        A_calc = calculateScatteringAMatrix(W2, Wg, V2, Vg);
        A_actual = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        assertAlmostEqual(A_actual, A_calc, absoluteTolerance, relativeTolerance);

    def testBMatrix(self):
        """
        Tests the B matrix (an intermediate matrix in calculating the scattering parameters for
        a given layer).
        """
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)
        kx = 1.0006;    # x component of k vector
        ky = 0.4247;    # y component of k vector
        l0 = 2.7;       # Free-space wavelength
        k0 = 2.3271;    # Free-space wavenumber

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;
        L = 0.25*l0;
        W1 = complexIdentity(2);
        Wg = complexIdentity(2);
        V1 = complexArray([[0 - 0.4698j, 0 - 1.1040j],[0 + 2.0114j, 0 + 0.4698j]]);
        Vg = complexArray([[0 - 0.4250j, 0 - 1.1804j], [0 + 2.0013j, 0 + 0.4250j]]);

        B_calc = calculateScatteringBMatrix(W1, Wg, V1, Vg);
        B_actual = complexArray([[-0.0049, 0.0427],[0.0427, -0.0873]]);
        assertAlmostEqual(B_actual, B_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;
        L = 0.5*l0;

        W2 = complexIdentity(2);
        Wg = complexIdentity(2);
        V2 = complexArray([[0 - 0.1051j, 0 - 0.4941j],[0 + 0.6970j, 0 + 0.1051j]]);
        Vg = complexArray([[0 - 0.4250j, 0 - 1.1804j],[0 + 2.0013j, 0 + 0.4250j]]);

        B_calc = calculateScatteringBMatrix(W2, Wg, V2, Vg);
        B_actual = complexArray([[-1.8324, -0.2579],[-0.2579, -1.3342]]);
        assertAlmostEqual(B_actual, B_calc, absoluteTolerance, relativeTolerance);

    def testDiMatrix(self):
        """
        Tests the composite D matrix (one of the matrices we use directly in the calculation
        of scattering matrices. At this point, we have to make a decision. Unfortunately since we
        only have the intermediate matrices to 4 decimal places, and we only have this matrix to
        4 decimal places (and it contains some nearly-zero terms), we are going to incur appreciable
        error. For now, I will tolerate that error, because we have one test case that we can test
        to 4 decimal places.
        """
        absoluteTolerance = 0.003;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.1; # Relative error tolerance (probably not necessary)
        kx = 1.0006;    # x component of k vector
        ky = 0.4247;    # y component of k vector
        l0 = 2.7;       # Free-space wavelength
        k0 = 2.3271;    # Free-space wavenumber

        # LAYER 1 DATA
        er = 2.0;
        ur = 1.0;
        kz = 0.9046;
        A = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        B = complexArray([[-0.0049, 0.0427], [0.0427, -0.0873]]);
        X = complexArray([[0.1493 + 0.9888j, 0+0j],[0+0j, 0.4193 + 0.9888j]]);

        D_calc = calculateScatteringDMatrix(A, B, X);
        D_actual = complexArray([[2.0057 - 0.0003j, -0.0445 + 0.0006j],[-0.0445 + 0.0006j, 2.0916 - 0.0013j]]);
        assertAlmostEqual(D_actual, D_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Since now we have the d-matrix to higher precision we can test it more strongly.
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)
        er = 1.0;
        ur = 3.0;
        kz = 1.3485;
        L = 0.5*l0;

        A = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        B = complexArray([[-1.8324, -0.2579], [-0.2579, -1.3342]]);
        X = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);

        D_calc = calculateScatteringDMatrix(A, B, X);
        D_actual = complexArray([[4.3436 - 0.7182j, 0.3604 - 0.1440j], [0.3604 - 0.1440j, 3.6475 - 0.4401j]]);
        assertAlmostEqual(D_actual, D_calc, absoluteTolerance, relativeTolerance);

    def testS11i(self):
        """
        Tests the S11 element of an inner layer (the ith layer)
        """
        absoluteTolerance = 0.03;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 1; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA
        A = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        B = complexArray([[-0.0049, 0.0427], [0.0427, -0.0873]]);
        X = complexArray([[0.1493 + 0.9888j, 0+0j],[0+0j, 0.4193 + 0.9888j]]);
        D = complexArray([[2.0057 - 0.0003j, -0.0445 + 0.0006j],[-0.0445 + 0.0006j, 2.0916 - 0.0013j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D)
        S11_calc = S_calc[0,0];
        S11_actual = complexArray([[0.0039 - 0.0006j, -0.0398 + 0.0060j],[-0.0398 + 0.0060j, 0.0808 - 0.0121j]])
        assertAlmostEqual(S11_actual, S11_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Since now we have the S-matrix to higher precision we can test it more strongly.
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        A = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        B = complexArray([[-1.8324, -0.2579], [-0.2579, -1.3342]]);
        X = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);
        D = complexArray([[4.3436 - 0.7182j, 0.3604 - 0.1440j],[0.3604 - 0.1440j, 3.6475 - 0.4401j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D);
        S11_calc = S_calc[0,0];
        S11_actual = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        assertAlmostEqual(S11_actual, S11_calc, absoluteTolerance, relativeTolerance);

    def testS12i(self):
        """
        Tests the S11 element of an inner layer (the ith layer)
        """
        absoluteTolerance = 0.001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 1; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA
        A = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        B = complexArray([[-0.0049, 0.0427], [0.0427, -0.0873]]);
        X = complexArray([[0.1493 + 0.9888j, 0+0j],[0+0j, 0.4193 + 0.9888j]]);
        D = complexArray([[2.0057 - 0.0003j, -0.0445 + 0.0006j],[-0.0445 + 0.0006j, 2.0916 - 0.0013j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D)
        S12_calc = S_calc[0,1];
        S12_actual = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        assertAlmostEqual(S12_actual, S12_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Since now we have the S-matrix to higher precision we can test it more strongly.
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        A = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        B = complexArray([[-1.8324, -0.2579], [-0.2579, -1.3342]]);
        X = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);
        D = complexArray([
            [4.3436 - 0.7182j, 0.3604 - 0.1440j],
            [0.3604 - 0.1440j, 3.6475 - 0.4401j]])

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D);
        S12_calc = S_calc[0,1];
        S12_actual = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        assertAlmostEqual(S12_actual, S12_calc, absoluteTolerance, relativeTolerance);

    def testS21i(self):
        """
        Tests the S11 element of an inner layer (the ith layer)
        """
        absoluteTolerance = 0.001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 1; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA
        A = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        B = complexArray([[-0.0049, 0.0427], [0.0427, -0.0873]]);
        X = complexArray([[0.1493 + 0.9888j, 0+0j],[0+0j, 0.4193 + 0.9888j]]);
        D = complexArray([
            [2.0057 - 0.0003j, -0.0445 + 0.0006j],
            [-0.0445 + 0.0006j, 2.0916 - 0.0013j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D)
        S21_calc = S_calc[1,0];
        S21_actual = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        assertAlmostEqual(S21_actual, S21_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Since now we have the S-matrix to higher precision we can test it more strongly.
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        A = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        B = complexArray([[-1.8324, -0.2579], [-0.2579, -1.3342]]);
        X = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);
        D = complexArray([[4.3436 - 0.7182j, 0.3604 - 0.1440j],[0.3604 - 0.1440j, 3.6475 - 0.4401j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D);
        S21_calc = S_calc[1,0];
        S21_actual = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        assertAlmostEqual(S21_actual, S21_calc, absoluteTolerance, relativeTolerance);

    def testS22i(self):
        """
        Tests the S11 element of an inner layer (the ith layer)
        """
        absoluteTolerance = 0.03;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 1; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA
        A = complexArray([[2.0049, -0.0427], [-0.0427, 2.0873]]);
        B = complexArray([[-0.0049, 0.0427], [0.0427, -0.0873]]);
        X = complexArray([[0.1493 + 0.9888j, 0+0j],[0+0j, 0.4193 + 0.9888j]]);
        D = complexArray([[2.0057 - 0.0003j, -0.0445 + 0.0006j],[-0.0445 + 0.0006j, 2.0916 - 0.0013j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D);
        S22_calc = S_calc[1,1];
        S22_actual = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        assertAlmostEqual(S22_actual, S22_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Since now we have the S-matrix to higher precision we can test it more strongly.
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        A = complexArray([[3.8324, 0.2579],[0.2579, 3.3342]]);
        B = complexArray([[-1.8324, -0.2579], [-0.2579, -1.3342]]);
        X = complexArray([[-0.4583 - 0.8888j, 0+0j],[0+0j, -0.4583 - 0.8888j]]);
        D = complexArray([[4.3436 - 0.7182j, 0.3604 - 0.1440j],[0.3604 - 0.1440j, 3.6475 - 0.4401j]]);

        S_calc = calculateInternalSMatrixFromRaw(A, B, X, D);
        S22_calc = S_calc[1,1];
        S22_actual = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        assertAlmostEqual(S22_actual, S22_calc, absoluteTolerance, relativeTolerance);

    def testDRed(self):
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        S11A = complexZeros(2);
        S22A = complexZeros(2);
        S12A = np.identity(2);
        S21A = np.identity(2);

        S11B = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        S12B = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        S21B = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        S22B = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);

        Dred_calc = calculateRedhefferDMatrix(S12A, S22A, S11B)
        Dred_actual = complexArray([[1,0],[0,1]]);
        assertAlmostEqual(Dred_actual, Dred_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        S11A = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        S12A = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        S21A = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        S22A = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        S11B = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        S12B = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        S21B = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        S22B = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);

        Dred_calc = calculateRedhefferDMatrix(S12A, S22A, S11B)
        Dred_actual = complexArray([
            [0.1506 + 0.9886j, -0.0163 - 0.0190j],
            [-0.0163 - 0.0190j, 0.1822 + 1.0253j]]);
        assertAlmostEqual(Dred_actual, Dred_calc, absoluteTolerance, relativeTolerance);

    def testFRed(self):
        absoluteTolerance = 0.001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.01; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        S11A = complexZeros(2);
        S22A = complexZeros(2);
        S12A = np.identity(2);
        S21A = np.identity(2);

        S11B = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        S12B = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        S21B = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        S22B = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);

        Fred_calc = calculateRedhefferFMatrix(S22A, S11B, S21B)
        Fred_actual = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.148 + 0.9848j]]);
        assertAlmostEqual(Fred_actual, Fred_calc, absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        S11A = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        S12A = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        S21A = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        S22A = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        S11B = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        S12B = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        S21B = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        S22B = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);

        Fred_calc = calculateRedhefferFMatrix(S22A, S11B, S21B)
        Fred_actual = complexArray([
            [-0.2117 - 0.6413j, 0.0471 + 0.0518j],
            [0.0471 + 0.0518j, -0.3027 - 0.7414j]]);
        assertAlmostEqual(Fred_actual, Fred_calc, absoluteTolerance, relativeTolerance);

    def testRedhefferProductS11(self):
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        SA = complexZeros((2,2,2,2));
        SA[0,1] = complexIdentity(2);
        SA[1,0] = complexIdentity(2);

        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        SB[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        D = complexArray([
            [1,0],
            [0,1]]);
        F = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);

        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_actual[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_calc = calculateRedhefferProduct(SA, SB);
        assertAlmostEqual(SAB_actual[0,0], SAB_calc[0,0], absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        SA = complexZeros((2,2,2,2));
        SA[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SA[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        SB[0,1] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,0] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,1] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        D = complexArray([
            [0.1506 + 0.9886j, -0.0163 - 0.0190j],
            [-0.0163 - 0.0190j, 0.1822 + 1.0253j]]);
        F = complexArray([
            [-0.2117 - 0.6413j, 0.0471 + 0.0518j],
            [0.0471 + 0.0518j, -0.3027 - 0.7414j]]);

        SAB_calc = calculateRedhefferProduct(SA, SB);
        # THIS STILL NEEDS TO BE FILLED IN. IT'S THE LAST GLOBAL S-MATRIX.
        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [-0.5961 + 0.4214j, -0.0840 + 0.0085j],
            [-0.0840 + 0.0085j, -0.4339 + 0.4051j]]);
        SAB_actual[0,1] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,0] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,1] = complexArray([
            [0.6971 - 0.2216j, 0.0672 - 0.0211j],
            [0.0672 - 0.0211j, 0.5673 - 0.1808j]]);

        assertAlmostEqual(SAB_actual[0,0], SAB_calc[0,0], absoluteTolerance, relativeTolerance);

    def testRedhefferProductS12(self):
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        SA = complexZeros((2,2,2,2));
        SA[0,1] = np.identity(2);
        SA[1,0] = np.identity(2);

        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        SB[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        D = complexArray([
            [1,0],
            [0,1]]);
        F = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);

        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_actual[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_calc = calculateRedhefferProduct(SA, SB);
        assertAlmostEqual(SAB_actual[0,1], SAB_calc[0,1], absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        SA = complexZeros((2,2,2,2));
        SA[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SA[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        SB[0,1] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,0] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,1] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        D = complexArray([
            [0.1506 + 0.9886j, -0.0163 - 0.0190j],
            [-0.0163 - 0.0190j, 0.1822 + 1.0253j]]);
        F = complexArray([
            [-0.2117 - 0.6413j, 0.0471 + 0.0518j],
            [0.0471 + 0.0518j, -0.3027 - 0.7414j]]);

        SAB_calc = calculateRedhefferProduct(SA, SB);
        # THIS STILL NEEDS TO BE FILLED IN. IT'S THE LAST GLOBAL S-MATRIX.
        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [-0.5961 + 0.4214j, -0.0840 + 0.0085j],
            [-0.0840 + 0.0085j, -0.4339 + 0.4051j]]);
        SAB_actual[0,1] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,0] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,1] = complexArray([
            [0.6971 - 0.2216j, 0.0672 - 0.0211j],
            [0.0672 - 0.0211j, 0.5673 - 0.1808j]]);

        assertAlmostEqual(SAB_actual[0,1], SAB_calc[0,1], absoluteTolerance, relativeTolerance);

    def testRedhefferProductS21(self):
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        SA = complexZeros((2,2,2,2))
        SA[0,1] = complexIdentity(2);
        SA[1,0] = complexIdentity(2);

        SB = complexZeros((2,2,2,2))
        SB[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        SB[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        D = complexArray([
            [1,0],
            [0,1]]);
        F = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);

        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_actual[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_calc = calculateRedhefferProduct(SA, SB);
        assertAlmostEqual(SAB_actual[1,0], SAB_calc[1,0], absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        SA = complexZeros((2,2,2,2));
        SA[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SA[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        SB[0,1] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,0] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,1] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        D = complexArray([
            [0.1506 + 0.9886j, -0.0163 - 0.0190j],
            [-0.0163 - 0.0190j, 0.1822 + 1.0253j]]);
        F = complexArray([
            [-0.2117 - 0.6413j, 0.0471 + 0.0518j],
            [0.0471 + 0.0518j, -0.3027 - 0.7414j]]);

        SAB_calc = calculateRedhefferProduct(SA, SB);
        # THIS STILL NEEDS TO BE FILLED IN. IT'S THE LAST GLOBAL S-MATRIX.
        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [-0.5961 + 0.4214j, -0.0840 + 0.0085j],
            [-0.0840 + 0.0085j, -0.4339 + 0.4051j]]);
        SAB_actual[0,1] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,0] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,1] = complexArray([
            [0.6971 - 0.2216j, 0.0672 - 0.0211j],
            [0.0672 - 0.0211j, 0.5673 - 0.1808j]]);

        assertAlmostEqual(SAB_actual[1,0], SAB_calc[1,0], absoluteTolerance, relativeTolerance);

    def testRedhefferProductS22(self):
        absoluteTolerance = 0.0001;# Absolute error tolerance for test data (we only have it to 4 digits)
        relativeTolerance = 0.001; # Relative error tolerance (probably not necessary)

        # LAYER 1 DATA - This is the data 
        # Current global data. Before applying the Redheffer star product to
        # any values, S11/S22 should be zero and S12/S21 should be the identity.
        SA = complexZeros((2,2,2,2));
        SA[0,1] = np.identity(2);
        SA[1,0] = np.identity(2);

        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        SB[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SB[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        D = complexArray([
            [1,0],
            [0,1]]);
        F = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);

        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_actual[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SAB_actual[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SAB_calc = calculateRedhefferProduct(SA, SB);
        assertAlmostEqual(SAB_actual[1,1], SAB_calc[1,1], absoluteTolerance, relativeTolerance);

        # LAYER 2 DATA
        # Current global data. After applying the Redheffer star product once, we will end up
        # with a new set of values for the scattering matrix, which are given in the text.
        # They are the SG11/SG12/SG21/SG22 from the first layer (after the update)
        SA = complexZeros((2,2,2,2));
        SA[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])
        SA[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]])
        SA[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.006j, 0.0808 - 0.0121j]])

        # The S11/etc. for the second layer.
        SB = complexZeros((2,2,2,2));
        SB[0,0] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        SB[0,1] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,0] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SB[1,1] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        D = complexArray([
            [0.1506 + 0.9886j, -0.0163 - 0.0190j],
            [-0.0163 - 0.0190j, 0.1822 + 1.0253j]]);
        F = complexArray([
            [-0.2117 - 0.6413j, 0.0471 + 0.0518j],
            [0.0471 + 0.0518j, -0.3027 - 0.7414j]]);

        SAB_calc = calculateRedhefferProduct(SA, SB);
        # THIS STILL NEEDS TO BE FILLED IN. IT'S THE LAST GLOBAL S-MATRIX.
        SAB_actual = complexZeros((2,2,2,2));
        SAB_actual[0,0] = complexArray([
            [-0.5961 + 0.4214j, -0.0840 + 0.0085j],
            [-0.0840 + 0.0085j, -0.4339 + 0.4051j]]);
        SAB_actual[0,1] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,0] = complexArray([
            [0.6020 - 0.3046j, -0.0431 + 0.0534j],
            [-0.0431 + 0.0534j, 0.6852 - 0.4078j]]);
        SAB_actual[1,1] = complexArray([
            [0.6971 - 0.2216j, 0.0672 - 0.0211j],
            [0.0672 - 0.0211j, 0.5673 - 0.1808j]]);

        assertAlmostEqual(SAB_actual[1,1], SAB_calc[1,1], absoluteTolerance, relativeTolerance);

    def testSrefFull(self):
        # I generated this Aref myself.
        # Tolerances relaxed due to small elements in the matrix
        absoluteTolerance = 0.007;
        relativeTolerance = 0.03;
        Aref = complexArray([
            [1.86002, 0.113614],
            [0.115376, 1.64547]]);
        Bref = complexArray([
            [0.139976, -0.113614],
            [-0.115376, 0.354529]]);
        Sref_calc = calculateReflectionRegionSMatrixFromRaw(Aref, Bref);

        Sref_actual = complexZeros((2,2,2,2));
        Sref_actual[0,0] = complexArray([
            [-0.0800, 0.0761],
            [0.0761, -0.2269]]);
        Sref_actual[0,1] = complexArray([
            [1.0800, -0.0761],
            [-0.0761, 1.2269]]);
        Sref_actual[1,0] = complexArray([
            [0.9200, 0.0761],
            [0.0761, 0.7731]]);
        Sref_actual[1,1] = complexArray([
            [0.0800, -0.0761],
            [-0.0761, 0.2269]]);
        assertAlmostEqual(Sref_calc, Sref_actual, absoluteTolerance, relativeTolerance);

    def testStrnFull(self):
        """
        WARNING: THIS HAS TO BE MODIFIED AND SHOULD CURRENTLY BE AN INTEGRATION TEST. I DO NOT HAVE
        RAW INPUT DATA FOR THIS FUNCTION. I AM RELYING ON AIJ/BIJ, and VWX to generate my input.
        I STILL HAVE TO WRITE THIS DAMN TEST.
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;

        # I generated these myself from known-working Aij, Bij, Wtrn. They are now hard-coded.
        Atrn = complexArray([
            [1.660774, -0.0652574],
            [-0.06525902, 1.786816]]);
        Btrn = complexArray([
            [0.339226, 0.0652574],
            [0.06525902, 0.21318382]]);

        Strn_calc = calculateTransmissionRegionSMatrixFromRaw(Atrn, Btrn);

        Strn_actual = complexZeros((2,2,2,2));
        Strn_actual[0,0] = complexArray([
            [0.2060, 0.0440],
            [0.0440, 0.1209]]);
        Strn_actual[0,1] = complexArray([
            [0.7940, -0.0440],
            [-0.0440, 0.8791]]);
        Strn_actual[1,0] = complexArray([
            [1.2060, 0.0440],
            [0.0440, 1.1209]]);
        Strn_actual[1,1] = complexArray([
            [-0.2060, -0.0440],
            [-0.0440, -0.1209]]);
        assertAlmostEqual(Strn_actual, Strn_calc, absoluteTolerance, relativeTolerance);

    def testCalculateInternalSMatrix(self):
        """
        Tests the code that will actually compute our S-matrix from the fundamental parameters,
        instead of the intermediate matrices.
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;

        l0 = 2.7;
        k0 = 2.3271;
        kx = 1.00063;
        ky = 0.424741;

        er = [2.0, 1.0];
        ur = [1.0, 3.0];
        L = [0.25*l0, 0.5*l0];
        Wg = complexIdentity(2);
        Vg = complexArray([
            [0 - 0.4250j, 0 - 1.1804j],
            [0 + 2.0013j, 0 + 0.4250j]]);

        i = 0;
        SiCalculated = calculateInternalSMatrix(kx, ky, er[i], ur[i], k0, L[i], Wg, Vg);

        SiActual = complexZeros((2,2,2,2));
        SiActual[0,0] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);
        SiActual[0,1] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SiActual[1,0] = complexArray([
            [0.1490 + 0.9880j, 0.0005 + 0.0017j],
            [0.0005 + 0.0017j, 0.1480 + 0.9848j]]);
        SiActual[1,1] = complexArray([
            [0.0039 - 0.0006j, -0.0398 + 0.0060j],
            [-0.0398 + 0.0060j, 0.0808 - 0.0121j]]);

        assertAlmostEqual(SiActual, SiCalculated, absoluteTolerance, relativeTolerance);

        i = 1;
        SiCalculated = calculateInternalSMatrix(kx, ky, er[i], ur[i], k0, L[i], Wg, Vg);
        SiActual[0,0] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);
        SiActual[0,1] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SiActual[1,0] = complexArray([
            [-0.2093 - 0.6406j, 0.0311 + 0.0390j],
            [0.0311 + 0.0390j, -0.2693 - 0.7160j]]);
        SiActual[1,1] = complexArray([
            [0.6997 - 0.2262j, 0.0517 - 0.0014j],
            [0.0517-0.0014j, 0.5998 - 0.2235j]]);

        assertAlmostEqual(SiActual, SiCalculated, absoluteTolerance, relativeTolerance);

    def testCalculatedReflectionRegionSMatrix(self):
        """
        Unit test
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        Wg = complexIdentity(2);
        Vg = complexArray([
            [0 - 0.4250j, 0 - 1.1804j],
            [0 + 2.0013j, 0 + 0.4250j]]);

        kx = 1.0006;
        ky = 0.4247;
        er = 1.4;
        ur = 1.2;

        SCalculated = calculateReflectionRegionSMatrix(kx, ky, er, ur, Wg, Vg);
        SActual = complexZeros((2,2,2,2));
        SActual[0,0] = complexArray([
            [-0.0800, 0.0761],
            [0.0761, -0.2269]]);
        SActual[0,1] = complexArray([
            [1.0800, -0.0761],
            [-0.0761, 1.2269]]);
        SActual[1,0] = complexArray([
            [0.9200, 0.0761],
            [0.0761, 0.7731]]);
        SActual[1,1] = complexArray([
            [0.0800, -0.0761],
            [-0.0761, 0.2269]]);

        assertAlmostEqual(SActual, SCalculated, absoluteTolerance, relativeTolerance);

    def testCalculatedTransmissionRegionSMatrix(self):
        """
        Unit test
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        Wg = complexIdentity(2);
        Vg = complexArray([
            [0 - 0.4250j, 0 - 1.1804j],
            [0 + 2.0013j, 0 + 0.4250j]]);

        kx = 1.0006;
        ky = 0.4247;

        ur = 1.6;
        er = 1.8;
        SCalculated = calculateTransmissionRegionSMatrix(kx, ky, er, ur, Wg, Vg);
        SActual = complexZeros((2,2,2,2));
        SActual[0,0] = complexArray([
            [0.2060, 0.0440],
            [0.0440, 0.1209]]);
        SActual[0,1] = complexArray([
            [0.7940, -0.0440],
            [-0.0440, 0.8791]]);
        SActual[1,0] = complexArray([
            [1.2060, 0.0440],
            [0.0440, 1.1209]]);
        SActual[1,1] = complexArray([
            [-0.2060, -0.0440],
            [-0.0440, -0.1209]]);

        assertAlmostEqual(SActual, SCalculated, absoluteTolerance, relativeTolerance);

    def testCalculateRT(self):
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;

        kx = 1.00063;
        ky = 0.424741;
        kzReflectionRegion = 0.705933;
        kzTransmissionRegion = 1.3032;

        urReflectionRegion = 1.2;
        erReflectionRegion = 1.4;
        urTransmissionRegion = 1.6;
        erTransmissionRegion = 1.8;

        RActual = 0.4403;
        TActual = 0.5597;

        EReflected = complexArray([0.0519-0.2856j, -0.4324 + 0.0780j, 0.1866 + 0.3580j]);
        ETransmitted = complexArray([-0.0101 + 0.3577j, 0.4358 - 0.0820j, -0.1343 - 0.2480j]);

        (RCalculated, TCalculated) = calculateRT(kzReflectionRegion, kzTransmissionRegion,
                urReflectionRegion, urTransmissionRegion, EReflected, ETransmitted);
        assertAlmostEqual(RActual, RCalculated, absoluteTolerance, relativeTolerance);
        assertAlmostEqual(TActual, TCalculated, absoluteTolerance, relativeTolerance);

    def itestGlobalScatteringMatrix(self):
        """
        Tests that the global scattering matrix is correct for the overall structure. If this works,
        then pretty much everything should work.
        """
        absoluteTolerance = 0.0001;
        relativeTolerance = 0.001;
        pTE = 1/sqrt(2);
        pTM = (1j)/sqrt(2);

        l0 = 2.7;
        k0 = 2*np.pi / l0;
        thetaInDegrees = 57;
        phiInDegrees = 23;
        theta = np.pi / 180.0 * thetaInDegrees;
        phi = np.pi / 180.0 * phiInDegrees;

        er = [2.0, 1.0];
        ur = [1.0, 3.0];
        L = [0.25*l0, 0.5*l0];

        erReflectionRegion = 1.4;
        urReflectionRegion = 1.2;
        erTransmissionRegion = 1.8;
        urTransmissionRegion = 1.6;

        # First, calculate the incident k-vector
        kVector = calculateKVector(theta, phi, erReflectionRegion, urReflectionRegion);
        kx = kVector[0];
        ky = kVector[1];
        kzReflectionRegion = kVector[2];

        # Calculate gap medium parameters
        erGap = 1 + sq(kx) + sq(ky); # This can be anything, but this simplifies an intermediate matrix
        urGap = 1;
        kzGap = calculateKz(kx, ky, erGap, urGap); # Should be 1.
        (Vg, Wg) = calculateVWXMatrices(kx, ky, kzGap, erGap, urGap);
        # THIS PART LOOKS GOOD.

        # Initialize the global scattering matrix
        Sglobal = complexZeros((2,2,2,2));
        Sglobal[1,0] = complexIdentity(2);
        Sglobal[0,1] = complexIdentity(2);

        # Now, loop through the layers - THIS PART MATCHES WHAT WE WANT.
        # BOTH THE SGLOBAL MATRICES AND THE SI MATRICES MATCH WHAT THEY SHOULD.
        numberOfLayers = len(L);
        for i in range(numberOfLayers):
            Si = calculateInternalSMatrix(kx, ky, er[i], ur[i], k0, L[i], Wg, Vg);

            # Finally, compute the redheffer product with the current global matrix
            Sglobal = calculateRedhefferProduct(Sglobal, Si);

        # Calculate the reflection and transmission region s matrices
        SReflectionRegion = calculateReflectionRegionSMatrix(kx, ky,
                erReflectionRegion, urReflectionRegion, Wg, Vg);
        # THE TRANSMISSION REGION MATRIX LOOKS WRONG.
        STransmissionRegion = calculateTransmissionRegionSMatrix(kx, ky,
                erTransmissionRegion, urTransmissionRegion, Wg, Vg);

        # Finally, compute the redheffer star product to connect our global matrix to the external
        # regions
        Sglobal = calculateRedhefferProduct(Sglobal, STransmissionRegion);
        Sglobal = calculateRedhefferProduct(SReflectionRegion, Sglobal);

        SGlobalCalculated = Sglobal;

        SGlobalActual = complexZeros((2,2,2,2));
        SGlobalActual[0,0] = complexArray([
            [-0.6018 + 0.3062j, -0.0043 + 0.0199j],
            [-0.0043 + 0.0199j, -0.5935 + 0.2678j]]);
        SGlobalActual[0,1] = complexArray([
            [0.5766 - 0.3110j, -0.0919 + 0.0469j],
            [-0.0919 + 0.0469j, 0.7542 - 0.4016j]]);
        SGlobalActual[1,0] = complexArray([
            [0.7415 - 0.4007j, 0.0716 - 0.0409j],
            [0.0716 - 0.0409j, 0.6033 - 0.3218j]]);
        SGlobalActual[1,1] = complexArray([
            [0.5861 - 0.3354j, 0.0170 + 0.0042j],
            [0.0170 + 0.0042j, 0.5533 - 0.3434j]]);

        assertAlmostEqual(SGlobalCalculated, SGlobalActual, absoluteTolerance, relativeTolerance);

    def setupData1x1Harmonics(self):
        cm = 1e-2
        deg = pi / 180
        self.lambda0 = 2 * cm
        self.theta = 0 * deg
        self.phi = 0 * deg
        self.pTE = 1
        self.pTM = 0

        self.urReflectionRegion = 1.0
        self.erReflectionRegion = 2.0
        self.urTransmissionRegion = 1.0
        self.erTransmissionRegion = 9.0
        self.erDeviceRegion = 6.0
        self.urDeviceRegion = 1.0
        self.xPeriod = 1.75 * cm
        self.yPeriod = 1.5 * cm
        thicknessLayer1 = 0.5 * cm
        thicknessLayer2 = 0.3 * cm

        self.Nx = 512;
        self.Ny = round(self.Nx * self.yPeriod / self.xPeriod);
        (spatialHarmonicsX, spatialHarmonicsY) = (1, 1)
        self.numberHarmonics = (spatialHarmonicsX, spatialHarmonicsY)

        self.dx = self.xPeriod / self.Nx;
        self.dy = self.yPeriod / self.Ny;
        self.xCoors = np.linspace(-self.xPeriod/2 + self.dx/2, self.xPeriod/2 - self.dx/2, self.Nx)
        self.yCoors = np.linspace(-self.yPeriod/2 + self.dy/2, self.yPeriod/2 - self.dy/2, self.Ny)

        self.triangleWidth = 0.8 * self.xPeriod
        self.triangleHeight = 0.5 * sqrt(3) * self.triangleWidth

        # NOTE - this assumes that our matrices have the x component as the 2nd index and the y component
        # as the third, for ease of indexing. [layer][x][y]
        self.urData = self.urDeviceRegion * complexOnes((2, self.Nx, self.Ny))
        self.erData = self.erDeviceRegion * complexOnes((2, self.Nx, self.Ny))
        triangleData = np.transpose(np.loadtxt('test/triangleData.csv', delimiter=','))
        self.erData[0] = triangleData;
        self.layerThickness = [thicknessLayer1, thicknessLayer2]

    def setupData3x3Harmonics(self):
        self.setupData1x1Harmonics() # data is equal to the old stuff, with some changes.
        numberHarmonicsX = 3
        numberHarmonicsY = 3
        self.numberHarmonics = (numberHarmonicsX, numberHarmonicsY)

        self.erConvolutionMatrixLayer1 = numpyArrayFromFile(
            "test/matrixDataNormal/layer1/erConvolutionData.txt")
        self.urConvolutionMatrixLayer1 = complexIdentity(9)
        self.erConvolutionMatrixLayer2 = 6*complexIdentity(9)
        self.urConvolutionMatrixLayer2 = complexIdentity(9)
        self.Kx = np.diag(1.1429*complexArray([1,0,-1,1,0,-1,1,0,-1]))
        self.Ky = np.diag(1.3333*complexArray([1,1,1,0,0,0,-1,-1,-1]))
        self.KzReflectionRegion = numpyArrayFromFile(
                "test/matrixDataNormal/reflectionRegion/KzReflectionRegion.txt")
        self.KzTransmissionRegion = np.diag(complexArray([2.4324, 2.6874, 2.4324, 2.7738, 3.0, 2.7738,
            2.4324, 2.6874, 2.4324]))

        self.KzFreeSpace = numpyArrayFromFile("test/matrixDataNormal/freeSpace/KzFreeSpace.txt")
        self.QFreeSpace = numpyArrayFromFile("test/matrixDataNormal/freeSpace/QFreeSpace.txt")
        self.WFreeSpace = complexIdentity(18)
        self.LamFreeSpace = numpyArrayFromFile("test/matrixDataNormal/freeSpace/LamFreeSpace.txt")
        self.VFreeSpace = numpyArrayFromFile("test/matrixDataNormal/freeSpace/VFreeSpace.txt")

        self.S11Transparent = complexZeros((18, 18))
        self.S22Transparent = complexZeros((18, 18))
        self.S21Transparent = complexIdentity(18)
        self.S12Transparent = complexIdentity(18)

        self.PLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/PLayer1.txt")
        self.QLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/QLayer1.txt")
        self.OmegaSquaredLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/OmegaSquaredLayer1.txt")
        self.LambdaLayer1= numpyArrayFromFile("test/matrixDataNormal/layer1/LambdaLayer1.txt")
        self.VLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/VLayer1.txt")
        self.ALayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/ALayer1.txt")
        self.BLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/BLayer1.txt")
        self.XLayer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/XLayer1.txt")
        self.S11Layer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/S11Layer1.txt")
        self.S12Layer1 = numpyArrayFromFile("test/matrixDataNormal/layer1/S12Layer1.txt")
        self.S21Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer1/S21Layer1.txt")
        self.S22Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer1/S22Layer1.txt")
        self.SGlobal11Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer1/SGlobal11Layer1.txt")
        self.SGlobal12Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer1/SGlobal12Layer1.txt")
        self.SGlobal21Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer1/SGlobal21Layer1.txt")
        self.SGlobal22Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer1/SGlobal22Layer1.txt")

        self.PLayer2 = numpyArrayFromFile("test/matrixDataNormal/layer2/PLayer2.txt")
        self.QLayer2 = numpyArrayFromFile("test/matrixDataNormal/layer2/QLayer2.txt")
        self.OmegaSquaredLayer2 = numpyArrayFromFile("test/matrixDataNormal/layer2/OmegaSquaredLayer2.txt")
        self.WLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/WLayer2.txt")
        self.LambdaLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/LambdaLayer2.txt")
        self.VLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/VLayer2.txt")
        self.ALayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/ALayer2.txt")
        self.BLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/BLayer2.txt")
        self.XLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/XLayer2.txt")
        self.S11Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/S11Layer2.txt")
        self.S12Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/S12Layer2.txt")
        self.S21Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/S21Layer2.txt")
        self.S22Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataNormal/layer2/S22Layer2.txt")
        self.SGlobal11Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer2/SGlobal11Layer2.txt")
        self.SGlobal12Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer2/SGlobal12Layer2.txt")
        self.SGlobal21Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer2/SGlobal21Layer2.txt")
        self.SGlobal22Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/layer2/SGlobal22Layer2.txt")

        self.QReflectionRegion = numpyArrayFromFile(
                "test/matrixDataNormal/reflectionRegion/QReflectionRegion.txt")
        self.LambdaReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/LambdaReflectionRegion.txt")
        self.WReflectionRegion = complexIdentity(18)
        self.VReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/VReflectionRegion.txt")
        self.LambdaReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/LambdaReflectionRegion.txt")
        self.AReflectionRegion= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/AReflectionRegion.txt")
        self.BReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/BReflectionRegion.txt")
        self.S11ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/S11ReflectionRegion.txt")
        self.S12ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/S12ReflectionRegion.txt")
        self.S21ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/S21ReflectionRegion.txt")
        self.S22ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/reflectionRegion/S22ReflectionRegion.txt")

        self.QTransmissionRegion = numpyArrayFromFile(
                "test/matrixDataNormal/transmissionRegion/QTransmissionRegion.txt")
        self.LambdaTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/LambdaTransmissionRegion.txt")
        self.WTransmissionRegion = complexIdentity(18)
        self.VTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/VTransmissionRegion.txt")
        self.LambdaTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/LambdaTransmissionRegion.txt")
        self.ATransmissionRegion= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/ATransmissionRegion.txt")
        self.BTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/BTransmissionRegion.txt")
        self.S11TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/S11TransmissionRegion.txt")
        self.S12TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/S12TransmissionRegion.txt")
        self.S21TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/S21TransmissionRegion.txt")
        self.S22TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/transmissionRegion/S22TransmissionRegion.txt")

        self.SGlobal11= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/SGlobal11.txt")
        self.SGlobal12= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/SGlobal12.txt")
        self.SGlobal21= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/SGlobal21.txt")
        self.SGlobal22= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataNormal/SGlobal22.txt")
        self.delta = complexArray([0,0,0,0,1,0,0,0,0])
        # TODO: add final csrc, esrc, cref, reflection coefficients, and so on

    def setupData3x3HarmonicsOblique(self):
        self.setupData1x1Harmonics() # data is equal to the old stuff, with some changes.
        numberHarmonicsX = 3
        numberHarmonicsY = 3
        self.numberHarmonics = (numberHarmonicsX, numberHarmonicsY)

        self.erConvolutionMatrixLayer1 = numpyArrayFromFile(
            "test/matrixDataOblique/layer1/erConvolutionData.txt")
        self.urConvolutionMatrixLayer1 = complexIdentity(9)
        self.erConvolutionMatrixLayer2 = 6*complexIdentity(9)
        self.urConvolutionMatrixLayer2 = complexIdentity(9)
        self.Kx = np.diag(complexArray(
            [2.2035, 1.0607, -0.0822, 2.2035, 1.0607, -0.0822, 2.2035, 1.0607, -0.0822]))
        self.Ky = np.diag(complexArray(
            [1.9457, 1.9457, 1.9457, 0.6124, 0.6124, 0.6124, -0.7210, -0.7210, -0.7210]))
        self.KzReflectionRegion = numpyArrayFromFile(
                "test/matrixDataOblique/reflectionRegion/KzReflectionRegion.txt")
        self.KzTransmissionRegion = np.diag(complexArray(
            [0.5989, 2.0222, 2.2820, 1.9415, 2.7386, 2.9357, 1.9039, 2.7121, 2.9109]))

        self.KzFreeSpace = numpyArrayFromFile(
                "test/matrixDataOblique/freeSpace/KzFreeSpace.txt")
        self.QFreeSpace = numpyArrayFromFile("test/matrixDataOblique/freeSpace/QFreeSpace.txt")
        self.WFreeSpace = complexIdentity(18)
        self.LambdaFreeSpace = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/freeSpace/LambdaFreeSpace.txt")
        self.VFreeSpace = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/freeSpace/VFreeSpace.txt")

        self.S11Transparent = complexZeros((18, 18))
        self.S22Transparent = complexZeros((18, 18))
        self.S21Transparent = complexIdentity(18)
        self.S12Transparent = complexIdentity(18)

        self.PLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/PLayer1.txt")
        self.QLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/QLayer1.txt")
        self.OmegaSquaredLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/OmegaSquaredLayer1.txt")
        self.LambdaLayer1= numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/LambdaLayer1.txt")
        self.VLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/VLayer1.txt")
        self.ALayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/ALayer1.txt")
        self.BLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/BLayer1.txt")
        self.XLayer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/XLayer1.txt")
        self.S11Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/S11Layer1.txt")
        self.S12Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/S12Layer1.txt")
        self.S21Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/S21Layer1.txt")
        self.S22Layer1 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer1/S22Layer1.txt")
        self.SGlobal11Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer1/SGlobal11Layer1.txt")
        self.SGlobal12Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer1/SGlobal12Layer1.txt")
        self.SGlobal21Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer1/SGlobal21Layer1.txt")
        self.SGlobal22Layer1 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer1/SGlobal22Layer1.txt")

        self.PLayer2 = numpyArrayFromFile("test/matrixDataOblique/layer2/PLayer2.txt")
        self.QLayer2 = numpyArrayFromFile("test/matrixDataOblique/layer2/QLayer2.txt")
        self.OmegaSquaredLayer2 = numpyArrayFromFile("test/matrixDataOblique/layer2/OmegaSquaredLayer2.txt")
        self.WLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/WLayer2.txt")
        self.LambdaLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/LambdaLayer2.txt")
        self.VLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/VLayer2.txt")
        self.ALayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/ALayer2.txt")
        self.BLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/BLayer2.txt")
        self.XLayer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/XLayer2.txt")
        self.S11Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/S11Layer2.txt")
        self.S12Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/S12Layer2.txt")
        self.S21Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/S21Layer2.txt")
        self.S22Layer2 = numpyArrayFromSeparatedColumnsFile("test/matrixDataOblique/layer2/S22Layer2.txt")
        self.SGlobal11Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer2/SGlobal11Layer2.txt")
        self.SGlobal12Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer2/SGlobal12Layer2.txt")
        self.SGlobal21Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer2/SGlobal21Layer2.txt")
        self.SGlobal22Layer2 = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/layer2/SGlobal22Layer2.txt")

        self.QReflectionRegion = numpyArrayFromFile(
                "test/matrixDataOblique/reflectionRegion/QReflectionRegion.txt")
        self.LambdaReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/LambdaReflectionRegion.txt")
        self.WReflectionRegion = complexIdentity(18)
        self.VReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/VReflectionRegion.txt")
        self.LambdaReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/LambdaReflectionRegion.txt")
        self.AReflectionRegion= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/AReflectionRegion.txt")
        self.BReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/BReflectionRegion.txt")
        self.S11ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/S11ReflectionRegion.txt")
        self.S12ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/S12ReflectionRegion.txt")
        self.S21ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/S21ReflectionRegion.txt")
        self.S22ReflectionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/reflectionRegion/S22ReflectionRegion.txt")

        self.QTransmissionRegion = numpyArrayFromFile(
                "test/matrixDataOblique/transmissionRegion/QTransmissionRegion.txt")
        self.LambdaTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/LambdaTransmissionRegion.txt")
        self.WTransmissionRegion = complexIdentity(18)
        self.VTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/VTransmissionRegion.txt")
        self.LambdaTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/LambdaTransmissionRegion.txt")
        self.ATransmissionRegion= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/ATransmissionRegion.txt")
        self.BTransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/BTransmissionRegion.txt")
        self.S11TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/S11TransmissionRegion.txt")
        self.S12TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/S12TransmissionRegion.txt")
        self.S21TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/S21TransmissionRegion.txt")
        self.S22TransmissionRegion = numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/transmissionRegion/S22TransmissionRegion.txt")

        self.SGlobal11= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/SGlobal11.txt")
        self.SGlobal12= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/SGlobal12.txt")
        self.SGlobal21= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/SGlobal21.txt")
        self.SGlobal22= numpyArrayFromSeparatedColumnsFile(
                "test/matrixDataOblique/SGlobal22.txt")

def main():
    test_class = Test(); # Create a new test class
    if(test_class.unitTestsEnabled == True):
        test_class.runUnitTests();
    if(test_class.integrationTestsEnabled == True):
        test_class.runIntegrationTests();
    test_class.printResults();

main();