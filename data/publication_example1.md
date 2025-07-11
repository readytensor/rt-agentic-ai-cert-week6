Variational auto-encoders (VAEs) are a type of generative model that can learn to encode input data into a latent space and then decode it back to reconstruct the original data.

VAEs are particularly useful for anomaly detection tasks on datasets like MNIST. They can also be used for synthetic data generation and missing data imputation.

They are based on the principles of variational inference and are trained to minimize the difference between the input data and the reconstructed output, while also regularizing the latent space to follow a specific distribution (usually Gaussian).

You can use PyTorch to implement VAEs.
