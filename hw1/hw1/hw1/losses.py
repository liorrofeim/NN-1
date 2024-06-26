import abc
import torch


class ClassifierLoss(abc.ABC):
    """
    Represents a loss function of a classifier.
    """

    def __call__(self, *args, **kwargs):
        return self.loss(*args, **kwargs)

    @abc.abstractmethod
    def loss(self, *args, **kw):
        pass

    @abc.abstractmethod
    def grad(self):
        """
        :return: Gradient of the last calculated loss w.r.t. model
            parameters, as a Tensor of shape (D, C).
        """
        pass


class SVMHingeLoss(ClassifierLoss):
    def __init__(self, delta=1.0):
        self.delta = delta
        self.grad_ctx = {}

    def loss(self, x, y, x_scores, y_predicted):
        """
        Calculates the Hinge-loss for a batch of samples.

        :param x: Batch of samples in a Tensor of shape (N, D).
        :param y: Ground-truth labels for these samples: (N,)
        :param x_scores: The predicted class score for each sample: (N, C).
        :param y_predicted: The predicted class label for each sample: (N,).
        :return: The classification loss as a Tensor of shape (1,).
        """

        assert x_scores.shape[0] == y.shape[0]
        assert y.dim() == 1

        # TODO: Implement SVM loss calculation based on the hinge-loss formula.
        #  Notes:
        #  - Use only basic pytorch tensor operations, no external code.
        #  - Full credit will be given only for a fully vectorized
        #    implementation (zero explicit loops).
        #    Hint: Create a matrix M where M[i,j] is the margin-loss
        #    for sample i and class j (i.e. s_j - s_{y_i} + delta).

        loss = None
        # ====== YOUR CODE: ======
        N = x_scores.size(0)
        # Gather the scores for the correct classes according to y
        correct_class_scores = x_scores[torch.arange(N), y].view(-1, 1)  # Shape (N, 1)

        # Calculate margins for all class scores with respect to the correct class scores
        margins = x_scores - correct_class_scores + self.delta

        # Ensure the margin for the correct class is 0
        margins[torch.arange(N), y] = 0

        # Calculate the hinge loss
        loss = torch.max(margins, torch.zeros_like(margins)).sum() / N
        # ========================

        # TODO: Save what you need for gradient calculation in self.grad_ctx
        # ====== YOUR CODE: ======
        self.grad_ctx = {
            'x': x,
            'y': y,
            'x_scores': x_scores,
            'y_predicted': y_predicted,
            'margins': margins
        }

        # ========================

        return loss

    def grad(self):
        """
        Calculates the gradient of the Hinge-loss w.r.t. parameters.
        :return: The gradient, of shape (D, C).

        """
        # TODO:
        #  Implement SVM loss gradient calculation
        #  Same notes as above. Hint: Use the matrix M from above, based on
        #  it create a matrix G such that X^T * G is the gradient.

        grad = None
        # ====== YOUR CODE: ======
        N = self.grad_ctx['x'].size(0)
        # Create a binary mask indicating which margins are greater than 0
        binary_mask = (self.grad_ctx['margins'] > 0).float()
        # Count the number of positive margins for each sample
        num_positive_margins = binary_mask.sum(dim=1, keepdim=True)
        # Subtract 1 from the binary mask for the correct class
        binary_mask[torch.arange(N), self.grad_ctx['y']] -= num_positive_margins.squeeze()
        # Multiply the binary mask by the input samples to get the gradient
        grad = torch.mm(self.grad_ctx['x'].t(), binary_mask) / N
        # ========================

        return grad
